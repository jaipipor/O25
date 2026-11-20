"""Full-744 continuous-geometry evaluation by sequential PCHIP."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.interpolate import PchipInterpolator
from .lookup import GEOMETRY_TOLERANCE_DEG, canonical_geometry, exact_node_lookup
from .model import BH4Model, load_model

@dataclass(frozen=True)
class GeometryResult:
    quantiles: np.ndarray
    requested_geometry: np.ndarray
    canonical_geometry: np.ndarray
    geometry_mode: str
    interpolation_used: bool
    geometry_index: int | None
    support: int | None
    minimum_raw_increment: float
    maximum_increment_floor_adjustment: float

def _ro(x, dtype=np.float64):
    a=np.array(x,dtype=dtype,copy=True); a.setflags(write=False); return a

def _nodes(model):
    return tuple(np.unique(model.geometries[:,i]) for i in range(3))

_TENSOR_CACHE = {}

def _tensor(model):
    key = id(model)
    cached = _TENSOR_CACHE.get(key)
    if cached is not None and cached[0] is model:
        return cached[1]
    sza,vza,raa=_nodes(model)
    q=model.absolute_relative_error_quantiles
    inc=q.copy(); inc[:,:,:,1:]=np.diff(q,axis=3); inc=np.maximum(inc,0)
    t=np.full((4,len(sza),len(vza),len(raa),12,9),np.nan)
    for gi,g in enumerate(model.geometries):
        i=np.searchsorted(sza,g[0]); j=np.searchsorted(vza,g[1]); k=np.searchsorted(raa,g[2])
        t[:,i,j,k]=inc[:,gi]
    for i,x in enumerate(sza):
        for j,y in enumerate(vza):
            if abs(x)<=1e-12 or abs(y)<=1e-12:
                t[:,i,j,1:]=t[:,i,j,0,None]
    if not np.all(np.isfinite(t)): raise RuntimeError('Expanded BH4 increment tensor contains missing values.')
    result = (sza, vza, raa, t)
    _TENSOR_CACHE[key] = (model, result)
    return result

def geometry_quantiles(class_id, geometry, model: BH4Model|None=None, tol_deg=GEOMETRY_TOLERANCE_DEG):
    """Evaluate 9-by-12 relative-error quantiles at any in-domain geometry."""
    model=load_model() if model is None else model
    requested=np.asarray(geometry,dtype=np.float64)
    g=canonical_geometry(geometry,tol_deg)
    sza,vza,raa,t=_tensor(model)
    for value,nodes,name in zip(g,(sza,vza,raa),('SZA','VZA','canonical RAA')):
        if value < nodes[0]-tol_deg or value > nodes[-1]+tol_deg:
            raise ValueError(f'{name}={value:g} is outside [{nodes[0]:g}, {nodes[-1]:g}].')
    try:
        e=exact_node_lookup(class_id,g,model,tol_deg)
        inc=np.vstack((e.quantiles[0],np.diff(e.quantiles,axis=0)))
        return GeometryResult(e.quantiles,_ro(requested),e.geometry,'direct',False,e.geometry_index,e.support,float(inc.min()),0.0)
    except ValueError as exc:
        from .lookup import GeometryNotFoundError
        if not isinstance(exc,GeometryNotFoundError): raise
    k=int(class_id)-1
    a=PchipInterpolator(raa,t[k],axis=2)(g[2])
    b=PchipInterpolator(vza,a,axis=1)(g[1])
    raw=PchipInterpolator(sza,b,axis=0)(g[0]).T
    scale=max(1.0,float(np.max(np.abs(raw)))); eps=64*np.spacing(scale)
    minimum=float(raw.min())
    if minimum < -eps: raise RuntimeError(f'PCHIP produced materially negative increment: {minimum:.17g}.')
    inc=np.maximum(raw,0); floor=float(np.max(np.abs(inc-raw))); q=np.cumsum(inc,axis=0)
    if q.shape!=(9,12) or not np.all(np.isfinite(q)) or np.any(np.diff(q,axis=0)<0):
        raise RuntimeError('Interpolated BH4 quantiles violate their numerical contract.')
    return GeometryResult(_ro(q),_ro(requested),g,'interpolated',True,None,None,minimum,floor)
