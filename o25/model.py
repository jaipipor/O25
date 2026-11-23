"""Class-based orchestration of O25 correction and BH4 uncertainty."""
from __future__ import annotations

from functools import lru_cache
import numpy as np

from ._applicability import assess_applicability
from ._core.coefficients import AngularCoefficients
from ._core.correction import correct_rrs
from ._core.iop import WaterOptics, retrieve_iops
from .bands import BAND_TOLERANCE_NM
from .bh4 import BH4Model, load_model as load_bh4_model, uncertainty_from_rrs
from .result import O25Result


class O25Model:
    """Reusable scientific model behind the simple :func:`o25.correct` frontend."""

    def __init__(self, coefficients=None, water=None, bh4_model=None):
        self.coefficients = coefficients or AngularCoefficients.from_package()
        self.water = water or WaterOptics.from_package()
        self.bh4_model = bh4_model or load_bh4_model()

    def _correct_o25(self, wl, Rrs, g0, g1):
        source = self.coefficients.evaluate(g0)
        target = self.coefficients.evaluate(g1)
        iops = retrieve_iops(wl, Rrs, self.water, source)
        Rrs_n = correct_rrs(iops.a, iops.bb, iops.bbw, iops.bbp, target)
        return iops.a, iops.bb, Rrs_n

    def correct(self, wl, Rrs, g0, g1=None, *, p=0.68, tol_nm=BAND_TOLERANCE_NM):
        wl = _spectrum(wl, "wl")
        Rrs = _spectrum(Rrs, "Rrs")
        if wl.size != Rrs.size:
            raise ValueError(f"wl and Rrs must have the same length; got {wl.size} and {Rrs.size}.")
        app = assess_applicability(wl, g0, g1, tol_nm)
        if not app.o25_available:
            raise ValueError(app.o25_message)
        a, bb, Rrs_n = self._correct_o25(wl, Rrs, app.source_geometry, app.target_geometry)
        if not app.bh4_available:
            return O25Result(a, bb, Rrs_n, app, uncertainty_status=app.bh4_status, uncertainty_message=app.bh4_message)
        try:
            bh4 = uncertainty_from_rrs(Rrs, wl, app.source_geometry, self.bh4_model)
        except ValueError as exc:
            return O25Result(a, bb, Rrs_n, app, uncertainty_status="bh4_input_outside_domain",
                uncertainty_message=f"O25 was applied, but BH4 uncertainty is unavailable: {exc}")
        p, j = _probability_index(bh4.probabilities, p)
        idx = app.bh4_bands.indices
        mask = np.zeros(wl.size, dtype=bool); mask[idx] = True
        u_rel = np.full(wl.size, np.nan, dtype=np.float64); u_rel[idx] = bh4.quantiles[0, :, j]
        u = u_rel * np.abs(Rrs_n)
        for x in (mask, u_rel, u): x.setflags(write=False)
        n_other = int(wl.size - mask.sum())
        message = (f"BH4 uncertainty at p={p:g} is provided at the 12 matched OLCI bands. "
                   f"{n_other} other wavelength(s) are NaN; spectral interpolation is not applied.")
        return O25Result(a, bb, Rrs_n, app, u, u_rel, int(bh4.class_id[0]), p, mask,
                         "available_native_olci", message, bh4)


def _spectrum(x, name):
    try: x = np.asarray(x, dtype=np.float64)
    except (TypeError, ValueError) as exc: raise ValueError(f"{name} must be a numeric one-dimensional array.") from exc
    if x.ndim != 1: raise ValueError(f"{name} must be a one-dimensional array.")
    if x.size == 0: raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(x)): raise ValueError(f"{name} must contain only finite values.")
    return x


def _probability_index(probabilities, p):
    try: p = float(p)
    except (TypeError, ValueError) as exc: raise ValueError("p must be one of the stored BH4 probabilities.") from exc
    i = np.flatnonzero(np.isclose(probabilities, p, rtol=0, atol=1e-12))
    if i.size != 1:
        values = ", ".join(f"{v:g}" for v in probabilities)
        raise ValueError(f"p must be one of the stored BH4 probabilities: {values}.")
    return p, int(i[0])


@lru_cache(maxsize=1)
def default_model() -> O25Model:
    return O25Model()
