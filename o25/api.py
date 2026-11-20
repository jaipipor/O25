"""Simple public frontend for O25 correction and BH4 uncertainty."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .model import O25Model
from ._applicability import Applicability, assess_applicability
from .bands import BAND_TOLERANCE_NM
from .bh4 import BH4Result, uncertainty_from_rrs

@dataclass(frozen=True)
class O25Result:
    """O25 outputs and, when available, native-band BH4 uncertainty."""
    a: np.ndarray
    bb: np.ndarray
    Rrs: np.ndarray
    applicability: Applicability
    u: np.ndarray | None = None
    u_rel: np.ndarray | None = None
    k: int | None = None
    p: float | None = None
    uncertainty_mask: np.ndarray | None = None
    uncertainty_status: str = "not_available"
    uncertainty_message: str = ""
    bh4: BH4Result | None = None

    @property
    def has_uncertainty(self) -> bool:
        return self.u is not None
    @property
    def g0(self) -> np.ndarray:
        return self.applicability.source_geometry
    @property
    def g1(self) -> np.ndarray:
        return self.applicability.target_geometry

def _spectrum(x: object, name: str) -> np.ndarray:
    try: x=np.asarray(x,dtype=np.float64)
    except (TypeError,ValueError) as exc: raise ValueError(f"{name} must be a numeric one-dimensional array.") from exc
    if x.ndim!=1: raise ValueError(f"{name} must be a one-dimensional array.")
    if x.size==0: raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(x)): raise ValueError(f"{name} must contain only finite values.")
    return x

def _probability_index(probabilities, p):
    try: p=float(p)
    except (TypeError,ValueError) as exc: raise ValueError("p must be one of the stored BH4 probabilities.") from exc
    i=np.flatnonzero(np.isclose(probabilities,p,rtol=0,atol=1e-12))
    if i.size!=1:
        values=", ".join(f"{v:g}" for v in probabilities)
        raise ValueError(f"p must be one of the stored BH4 probabilities: {values}.")
    return p,int(i[0])

def correct(wl: object, Rrs: object, g0: object, g1: object|None=None, *,
            p: float=0.68, tol_nm: float=BAND_TOLERANCE_NM) -> O25Result:
    """Correct Rrs from ``g0`` to ``g1`` and add BH4 uncertainty when valid.

    ``g1`` defaults to ``(0, 0, 0)``. BH4 is applied automatically only for
    that target and when all 12 bands are available. ``u_rel`` and ``u`` have
    the same length as ``wl``; non-BH4 wavelengths are explicitly ``NaN``.
    ``u = u_rel * abs(Rrs_corrected)`` at native BH4 bands.
    """
    wl=_spectrum(wl,"wl"); Rrs=_spectrum(Rrs,"Rrs")
    if wl.size!=Rrs.size: raise ValueError(f"wl and Rrs must have the same length; got {wl.size} and {Rrs.size}.")
    app=assess_applicability(wl,g0,g1,tol_nm)
    if not app.o25_available: raise ValueError(app.o25_message)
    a,bb,Rrs_n=O25Model()._correct_o25(wl,Rrs,app.source_geometry,app.target_geometry)
    a=np.asarray(a,dtype=np.float64); bb=np.asarray(bb,dtype=np.float64); Rrs_n=np.asarray(Rrs_n,dtype=np.float64)

    if not app.bh4_available:
        return O25Result(a,bb,Rrs_n,app,uncertainty_status=app.bh4_status,uncertainty_message=app.bh4_message)

    try:
        bh4=uncertainty_from_rrs(Rrs,wl,app.source_geometry)
    except ValueError as exc:
        return O25Result(a,bb,Rrs_n,app,uncertainty_status="bh4_input_outside_domain",
            uncertainty_message=f"O25 was applied, but BH4 uncertainty is unavailable: {exc}")

    p,j=_probability_index(bh4.probabilities,p)
    idx=app.bh4_bands.indices
    mask=np.zeros(wl.size,dtype=bool); mask[idx]=True
    u_rel=np.full(wl.size,np.nan,dtype=np.float64)
    u_rel[idx]=bh4.quantiles[0,:,j]
    u=u_rel*np.abs(Rrs_n)
    for x in (mask,u_rel,u): x.setflags(write=False)
    n_other=int(wl.size-mask.sum())
    message=(f"BH4 uncertainty at p={p:g} is provided at the 12 matched OLCI bands. "
             f"{n_other} other wavelength(s) are NaN; spectral interpolation is not applied.")
    return O25Result(a,bb,Rrs_n,app,u,u_rel,int(bh4.class_id[0]),p,mask,
                     "available_native_olci",message,bh4)
