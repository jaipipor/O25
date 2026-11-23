"""Compatibility interface for scripts written for O25 0.1.x.

New code should use ``o25.correct(...)``.
"""

from __future__ import annotations

from .model import default_model


def O25_hyp(l, Rrs, geom_old, geom_new):
    """Return ``a``, ``bb`` and corrected ``Rrs`` using the class-based core."""
    result = default_model().correct(l, Rrs, geom_old, geom_new)
    return result.a, result.bb, result.Rrs


__all__ = ["O25_hyp"]
