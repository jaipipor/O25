"""Standalone spectrum-to-BH4-uncertainty engine."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .classifier import ClassResult, assign_class
from .features import FeatureResult, features_from_rrs
from .geometry import GeometryResult, geometry_quantiles
from .model import BH4Model, load_model

@dataclass(frozen=True)
class BH4Result:
    features: FeatureResult
    classification: ClassResult
    geometry: tuple[GeometryResult,...]
    class_id: np.ndarray
    wavelengths_nm: np.ndarray
    probabilities: np.ndarray
    quantiles: np.ndarray
    model_version: str

def _ro(x,dtype=np.float64):
    a=np.array(x,dtype=dtype,copy=True); a.setflags(write=False); return a

def uncertainty_from_rrs(Rrs, wl, geometry, model: BH4Model|None=None):
    """Return BH4 relative-error quantiles for one or many spectra."""
    model=load_model() if model is None else model
    f=features_from_rrs(Rrs,wl); c=assign_class(f.values,model)
    n=f.values.shape[0]
    g=np.asarray(geometry,dtype=np.float64)
    if g.shape==(3,): g=np.repeat(g[None,:],n,axis=0)
    if g.shape!=(n,3): raise ValueError('geometry must have shape (3,) or (N, 3) matching Rrs.')
    results=tuple(geometry_quantiles(int(c.class_id[i]),g[i],model) for i in range(n))
    q=np.stack([r.quantiles.T for r in results],axis=0) # N, wavelength, probability
    return BH4Result(f,c,results,c.class_id,_ro(model.wavelengths_nm),_ro(model.required_probabilities),_ro(q),model.version)
