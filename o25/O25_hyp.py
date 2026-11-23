"""Compatibility wrapper for the historical O25_hyp interface."""
from __future__ import annotations
from .model import default_model


def O25_hyp(l, Rrs, geom_old, geom_new):
    result = default_model().correct(l, Rrs, geom_old, geom_new)
    return result.a, result.bb, result.Rrs


__all__ = ["O25_hyp"]
