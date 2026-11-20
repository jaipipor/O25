"""Compatibility wrapper for the historical O25_hyp interface."""
from __future__ import annotations
from .model import O25Model

def O25_hyp(l, Rrs, geom_old, geom_new):
    """Return ``(a, bb, Rrs_corrected)`` using the maintained O25 kernel."""
    r = O25Model().correct(l, Rrs, geom_old, geom_new)
    return r.a, r.bb, r.Rrs

__all__ = ["O25_hyp"]
