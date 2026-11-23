"""Independent wavelength-band matching for O25 and BH4."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import linear_sum_assignment

BAND_TOLERANCE_NM = 5.0
O25_BANDS_NM = np.array([443.0, 490.0, 560.0, 665.0])
BH4_BANDS_NM = np.array([
    400.0, 412.0, 443.0, 490.0, 510.0, 560.0,
    620.0, 665.0, 673.0, 681.0, 709.0, 753.0,
])

@dataclass(frozen=True)
class BandMatch:
    required_nm: np.ndarray
    indices: np.ndarray
    matched_nm: np.ndarray
    delta_nm: np.ndarray

    @property
    def complete(self) -> bool:
        return bool(np.all(self.indices >= 0))

    @property
    def missing_nm(self) -> np.ndarray:
        return self.required_nm[self.indices < 0]


def _vector(x: object, name: str) -> np.ndarray:
    try:
        x = np.asarray(x, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain numeric wavelengths in nm.") from exc
    if x.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional wavelength array.")
    if x.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must contain only finite wavelengths.")
    if np.unique(x).size != x.size:
        raise ValueError(f"{name} contains duplicate wavelengths.")
    return x


def match_bands(wl: object, required_nm: object,
                tol_nm: float = BAND_TOLERANCE_NM) -> BandMatch:
    """Assign distinct observed wavelengths to nominal bands.

    The assignment maximizes the number of matches, then minimizes total
    absolute wavelength difference. The tolerance boundary is inclusive.
    """
    wl = _vector(wl, "wl")
    req = _vector(required_nm, "required_nm")
    try:
        tol = float(tol_nm)
    except (TypeError, ValueError) as exc:
        raise ValueError("tol_nm must be a finite non-negative number.") from exc
    if not np.isfinite(tol) or tol < 0:
        raise ValueError("tol_nm must be a finite non-negative number.")

    nr, nw = req.size, wl.size
    d = np.abs(req[:, None] - wl[None, :])
    miss = tol + 1.0
    invalid = miss * (nr + 1.0)
    cost = np.full((nr, nw + nr), miss)
    cost[:, :nw] = np.where(d <= tol, d, invalid)
    cost[:, :nw] += np.finfo(float).eps * max(1.0, tol) * np.arange(nw)

    rows, cols = linear_sum_assignment(cost)
    idx = np.full(nr, -1, dtype=np.int64)
    use = cols < nw
    use &= d[rows, np.minimum(cols, nw - 1)] <= tol
    idx[rows[use]] = cols[use]

    matched = np.full(nr, np.nan)
    delta = np.full(nr, np.nan)
    ok = idx >= 0
    matched[ok] = wl[idx[ok]]
    delta[ok] = matched[ok] - req[ok]
    for a in (req, idx, matched, delta):
        a.setflags(write=False)
    return BandMatch(req, idx, matched, delta)


def match_o25_bands(wl: object, tol_nm: float = BAND_TOLERANCE_NM) -> BandMatch:
    return match_bands(wl, O25_BANDS_NM, tol_nm)


def match_bh4_bands(wl: object, tol_nm: float = BAND_TOLERANCE_NM) -> BandMatch:
    return match_bands(wl, BH4_BANDS_NM, tol_nm)
