"""Immutable results returned by the public O25 frontend."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from ._applicability import Applicability
from .bh4 import BH4Result


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
