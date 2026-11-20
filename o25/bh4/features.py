"""BH4 spectral features ported from ``bh4_features_from_rrs.m``."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import trapezoid

from ..bands import BAND_TOLERANCE_NM, match_bh4_bands

_AVW_MEAN = 470.7864431828539
_AVW_STD = 45.686803949699936
_AVW_COEF = np.array([
    0.009484225687080, -0.125857036467817, 0.633361746083368,
    -1.511567070824567, 1.540476993755809, 0.826691594671428,
    -2.542684738869314, -4.088200549057942, 7.613957716213165,
    -4.042838706303126,
], dtype=np.float64)
_REQUIRED_NM = np.array(
    [400, 412, 443, 490, 510, 560, 620, 665, 673, 681, 709, 753],
    dtype=np.float64,
)


@dataclass(frozen=True)
class FeatureResult:
    """BH4 features and the intermediate AVW information."""

    values: np.ndarray
    avw_discrete_nm: np.ndarray
    avw_corrected_nm: np.ndarray
    selected_indices: np.ndarray


def _readonly(a, dtype=np.float64):
    a = np.array(a, dtype=dtype, copy=True)
    a.setflags(write=False)
    return a


def features_from_rrs(Rrs, wl, tol_nm=BAND_TOLERANCE_NM) -> FeatureResult:
    """Calculate corrected AVW, visible area and NDI.

    ``Rrs`` may be one spectrum ``(L,)`` or several spectra ``(N, L)``.
    Wavelengths are matched uniquely to the 12 BH4 bands within ``tol_nm``.
    All calculations and returned floating-point values use double precision.
    """
    try:
        x = np.asarray(Rrs, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("Rrs must contain numeric values.") from exc
    if x.ndim == 1:
        x = x.reshape(1, -1)
    elif x.ndim != 2:
        raise ValueError("Rrs must be a one- or two-dimensional array.")
    if x.shape[1] != np.asarray(wl).size:
        raise ValueError("Rrs spectral length must equal the length of wl.")
    if not np.all(np.isfinite(x)):
        raise ValueError("Rrs must contain only finite values.")
    if np.any(x <= 0):
        raise ValueError("BH4 feature calculation requires strictly positive Rrs.")

    match = match_bh4_bands(wl, tol_nm)
    if not match.complete:
        missing = ", ".join(f"{v:g}" for v in match.missing_nm)
        raise ValueError(
            f"BH4 requires bands near {missing} nm within +/-{tol_nm:g} nm."
        )

    y = x[:, match.indices]
    avw0 = np.sum(y, axis=1) / np.sum(y / _REQUIRED_NM, axis=1)
    z = (avw0 - _AVW_MEAN) / _AVW_STD
    avw = avw0 + np.polyval(_AVW_COEF, z)

    # MATLAB: trapz([443 560 665], Rrs(:, [443 560 665]), 2)
    visible = trapezoid(y[:, [2, 5, 7]],_REQUIRED_NM[[2, 5, 7]],axis=1,)
    ndi = (y[:, 5] - y[:, 7]) / (y[:, 5] + y[:, 7])
    values = np.column_stack((avw, visible, ndi))

    return FeatureResult(
        values=_readonly(values),
        avw_discrete_nm=_readonly(avw0),
        avw_corrected_nm=_readonly(avw),
        selected_indices=_readonly(match.indices, np.int64),
    )
