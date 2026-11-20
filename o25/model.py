"""Reusable, stateless O25 model orchestration."""
from __future__ import annotations
from ._core.correction import O25_hyp as _O25_hyp

class O25Model:
    """Run O25 corrections while keeping implementation details private.

    Constructing a model is optional. It is useful for explicit dependency
    injection and repeated processing; ordinary users should call
    :func:`o25.correct`.
    """
    def correct(self, wl, Rrs, g0, g1=None, *, p=0.68, tol_nm=5.0):
        from .api import correct
        return correct(wl, Rrs, g0, g1, p=p, tol_nm=tol_nm)

    @staticmethod
    def _correct_o25(wl, Rrs, g0, g1):
        return _O25_hyp(wl.copy(), Rrs.copy(), g0.copy(), g1.copy())
