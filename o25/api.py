"""Simple public frontend for O25 correction."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .O25_hyp import O25_hyp
from .applicability import Applicability, assess_applicability
from .bands import BAND_TOLERANCE_NM


@dataclass(frozen=True)
class O25Result:
    """Outputs from an O25 correction.

    ``u`` and ``k`` are reserved for BH4 uncertainty and class. They remain
    ``None`` until the validated BH4 port is connected.
    """

    a: np.ndarray
    bb: np.ndarray
    Rrs: np.ndarray
    applicability: Applicability
    u: np.ndarray | None = None
    u_rel: np.ndarray | None = None
    k: int | None = None
    uncertainty_status: str = "not_available"
    uncertainty_message: str = ""

    @property
    def has_uncertainty(self) -> bool:
        return self.u is not None

    @property
    def g0(self) -> np.ndarray:
        return self.applicability.source_geometry

    @property
    def g1(self) -> np.ndarray:
        return self.applicability.target_geometry


def _spectrum(x: object, name: str) -> np.ndarray:
    try:
        x = np.asarray(x, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric one-dimensional array.") from exc
    if x.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array.")
    if x.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must contain only finite values.")
    return x


def correct(
    wl: object,
    Rrs: object,
    g0: object,
    g1: object | None = None,
    *,
    tol_nm: float = BAND_TOLERANCE_NM,
) -> O25Result:
    """Correct directional Rrs from geometry ``g0`` to ``g1``.

    If ``g1`` is omitted, ``(0, 0, 0)`` is used. BH4 eligibility is assessed,
    but uncertainty is not yet calculated because the validated BH4 port has
    not been connected.
    """
    wl = _spectrum(wl, "wl")
    Rrs = _spectrum(Rrs, "Rrs")
    if wl.size != Rrs.size:
        raise ValueError(
            f"wl and Rrs must have the same length; got {wl.size} and {Rrs.size}."
        )

    app = assess_applicability(wl, g0, g1, tol_nm)
    if not app.o25_available:
        raise ValueError(app.o25_message)

    a, bb, Rrs_n = O25_hyp(
        wl.copy(), Rrs.copy(),
        app.source_geometry.copy(), app.target_geometry.copy(),
    )
    a = np.asarray(a, dtype=np.float64)
    bb = np.asarray(bb, dtype=np.float64)
    Rrs_n = np.asarray(Rrs_n, dtype=np.float64)

    if app.bh4_available:
        u_status = "not_implemented"
        u_message = (
            "The spectrum and target geometry satisfy BH4 requirements, but "
            "the validated BH4 model has not yet been connected."
        )
    else:
        u_status = app.bh4_status
        u_message = app.bh4_message

    return O25Result(
        a=a,
        bb=bb,
        Rrs=Rrs_n,
        applicability=app,
        uncertainty_status=u_status,
        uncertainty_message=u_message,
    )
