"""Pure-water properties and O25 IOP retrieval."""
from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import as_file, files
import numpy as np
from scipy.interpolate import interp1d

from .coefficients import CoefficientValues

_P_CHI = -np.array(
    [0.140559039379002, 0.102529719530837,
     1.141618978662982, 1.258673459838637],
    dtype=np.float64,
)


def _readonly(x: np.ndarray) -> np.ndarray:
    x = np.array(x, dtype=np.float64, copy=True)
    x.setflags(write=False)
    return x


@dataclass(frozen=True)
class IOPResult:
    a: np.ndarray
    bb: np.ndarray
    bbw: np.ndarray
    bbp: np.ndarray


class WaterOptics:
    """Packaged pure-water absorption and backscattering table."""

    def __init__(self, wavelength_nm, aw, bw):
        self.wavelength_nm = _readonly(wavelength_nm)
        self.aw = _readonly(aw)
        self.bw = _readonly(bw)
        if not (self.wavelength_nm.shape == self.aw.shape == self.bw.shape):
            raise ValueError("Water-optics table columns must have equal lengths.")
        if np.any(np.diff(self.wavelength_nm) <= 0) or not np.all(np.isfinite(self.aw)) or not np.all(np.isfinite(self.bw)):
            raise ValueError("Water-optics table is invalid.")
        self._aw_interpolator = interp1d(self.wavelength_nm, self.aw, kind="linear", bounds_error=False, fill_value="extrapolate")
        self._bw_interpolator = interp1d(self.wavelength_nm, self.bw, kind="linear", bounds_error=False, fill_value="extrapolate")

    @classmethod
    def from_package(cls) -> "WaterOptics":
        resource = files("o25").joinpath(
            "data", "o25", "abs_scat_seawater_20d_35PSU_20230922_short.txt"
        )
        with as_file(resource) as path:
            table = np.loadtxt(path, comments="%", dtype=np.float64)
        table = table[:-1]  # terminal -1 sentinel in the historical table
        return cls(table[:, 0], table[:, 1], table[:, 2])

    def at(self, wavelength_nm) -> tuple[np.ndarray, np.ndarray]:
        wl = np.asarray(wavelength_nm, dtype=np.float64)
        aw = np.asarray(self._aw_interpolator(wl), dtype=np.float64)
        bw = np.asarray(self._bw_interpolator(wl), dtype=np.float64)
        return aw, bw


def _legacy_band_indices(wl: np.ndarray, Rrs: np.ndarray) -> tuple[np.ndarray, ...]:
    valid = np.isfinite(Rrs)
    return (
        np.flatnonzero((wl > 440) & (wl < 446) & valid),
        np.flatnonzero((wl > 487) & (wl < 493) & valid),
        np.flatnonzero((wl > 554) & (wl < 566) & valid),
        np.flatnonzero((wl > 662) & (wl < 668) & valid),
    )


def retrieve_iops(wl, Rrs, water: WaterOptics, source: CoefficientValues) -> IOPResult:
    """Retrieve total absorption and backscattering using the O25 equations."""
    wl = np.asarray(wl, dtype=np.float64)
    Rrs = np.asarray(Rrs, dtype=np.float64)
    aw, bbw = water.at(wl)
    i2, i3, i5, i6 = _legacy_band_indices(wl, Rrs)
    if any(index.size == 0 for index in (i2, i3, i5, i6)):
        raise ValueError("O25 numerical retrieval could not identify all four spectral regions.")
    R2, R3, R5, R6 = (float(np.mean(Rrs[index])) for index in (i2, i3, i5, i6))
    eta = 1.433 * (1 - 0.5091 * np.exp(-0.8671 * np.log10(R2 / R5)))
    chi = np.log10((R2 + R3) / (R5 + 5 * R6**2 / R3))
    aw0, bbw0 = float(np.mean(aw[i5])), float(np.mean(bbw[i5]))
    al0 = aw0 + 10 ** np.polyval(_P_CHI, chi)
    C0 = source.G0w * bbw0 * (al0 + bbw0) - R5 * (al0 + bbw0)**2 + source.G1w * bbw0**2
    C1 = source.G0w * bbw0 + source.G0p * (al0 + bbw0) - 2 * R5 * (al0 + bbw0)
    C2 = source.G0p + source.G1p - R5
    bbp0 = (np.sqrt(C1**2 - 4 * C2 * C0) - C1) / (2 * C2)
    bbp = bbp0 * (wl[i5[0]] / wl) ** eta
    bb = bbp + bbw
    D0 = source.G1w * bbw**2 + source.G1p * bbp**2
    D1 = source.G0w * bbw + source.G0p * bbp
    a = -(bbw + bbp) + (np.sqrt(D1**2 + 4 * Rrs * D0) + D1) / (2 * Rrs)
    return IOPResult(_readonly(a), _readonly(bb), _readonly(bbw), _readonly(bbp))
