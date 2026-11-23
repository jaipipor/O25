"""Bidirectional correction kernel for explicit O25 inputs."""
from __future__ import annotations
import numpy as np
from .coefficients import CoefficientValues


def correct_rrs(a, bb, bbw, bbp, target: CoefficientValues) -> np.ndarray:
    """Correct Rrs using retrieved IOPs and target-geometry coefficients."""
    a = np.asarray(a, dtype=np.float64)
    bb = np.asarray(bb, dtype=np.float64)
    bbw = np.asarray(bbw, dtype=np.float64)
    bbp = np.asarray(bbp, dtype=np.float64)
    k = a + bb
    corrected = (
        (target.G0w + target.G1w * bbw / k) * bbw / k
        + (target.G0p + target.G1p * bbp / k) * bbp / k
    )
    corrected = np.array(corrected, dtype=np.float64, copy=True)
    corrected.setflags(write=False)
    return corrected
