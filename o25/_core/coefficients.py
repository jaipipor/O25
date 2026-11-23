"""O25 angular-coefficient resources and interpolation."""
from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import as_file, files
import numpy as np
from scipy.interpolate import RegularGridInterpolator

_SZA = np.r_[np.arange(0.0, 81.0, 10.0), 87.5]
_VZA = _SZA.copy()
_RAA = np.arange(0.0, 181.0, 15.0)
_NAMES = ("G0w.txt", "G1w.txt", "G0p.txt", "G1p.txt")


def _readonly(x: np.ndarray) -> np.ndarray:
    x = np.array(x, dtype=np.float64, copy=True)
    x.setflags(write=False)
    return x


@dataclass(frozen=True)
class CoefficientValues:
    G0w: float
    G1w: float
    G0p: float
    G1p: float


class AngularCoefficients:
    """Loaded O25 angular tables with reusable trilinear interpolators."""

    def __init__(self, values: np.ndarray):
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (10, 10, 13, 4):
            raise ValueError(f"O25 coefficient tensor has shape {values.shape}; expected (10, 10, 13, 4).")
        if not np.all(np.isfinite(values)):
            raise ValueError("O25 coefficient tensor contains non-finite values.")
        self._values = _readonly(values)
        self._interpolators = tuple(
            RegularGridInterpolator(
                (_SZA, _VZA, _RAA), self._values[..., j],
                bounds_error=False, fill_value=None,
            )
            for j in range(4)
        )

    @classmethod
    def from_package(cls) -> "AngularCoefficients":
        root = files("o25").joinpath("data", "o25")
        tables = []
        for name in _NAMES:
            with as_file(root.joinpath(name)) as path:
                table = np.loadtxt(path, dtype=np.float64)
            if table.shape != (130, 10):
                raise ValueError(f"O25 table {name} has shape {table.shape}; expected (130, 10).")
            tables.append(table)
        values = np.empty((10, 10, 13, 4), dtype=np.float64)
        for iaz in range(13):
            rows = slice(10 * iaz, 10 * (iaz + 1))
            for j, table in enumerate(tables):
                values[:, :, iaz, j] = table[rows, :]
        return cls(values)

    @property
    def values(self) -> np.ndarray:
        return self._values

    def evaluate(self, geometry) -> CoefficientValues:
        g = np.asarray(geometry, dtype=np.float64)
        if g.shape != (3,) or not np.all(np.isfinite(g)):
            raise ValueError("geometry must contain three finite angles (SZA, VZA, RAA).")
        values = [interpolator(g).item() for interpolator in self._interpolators]
        return CoefficientValues(*values)
