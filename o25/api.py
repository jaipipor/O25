"""Very small public frontend for scientific use."""
from __future__ import annotations
from .bands import BAND_TOLERANCE_NM
from .model import default_model
from .result import O25Result


def correct(wl, Rrs, g0, g1=None, *, p=0.68, tol_nm=BAND_TOLERANCE_NM) -> O25Result:
    """Correct one Rrs spectrum and add BH4 uncertainty when applicable."""
    return default_model().correct(wl, Rrs, g0, g1, p=p, tol_nm=tol_nm)


__all__ = ["correct", "O25Result"]
