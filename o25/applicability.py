"""Applicability decisions for the future O25/BH4 frontend.

This module decides whether the spectral and target-geometry requirements are
met. It does not run O25 or BH4 and does not alter their numerical code.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .bands import BAND_TOLERANCE_NM, BandMatch, match_bh4_bands, match_o25_bands

DEFAULT_TARGET_GEOMETRY = np.array([0.0, 0.0, 0.0])
_TARGET_ATOL = 1e-12


@dataclass(frozen=True)
class Applicability:
    """Outcome of the O25 and BH4 applicability checks."""

    source_geometry: np.ndarray
    target_geometry: np.ndarray
    target_was_defaulted: bool
    o25_bands: BandMatch
    bh4_bands: BandMatch
    o25_available: bool
    bh4_available: bool
    o25_status: str
    bh4_status: str
    o25_message: str
    bh4_message: str


def _geometry(g: object, name: str) -> np.ndarray:
    try:
        g = np.asarray(g, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{name} must contain three numeric angles: (ths, thv, phi)."
        ) from exc
    if g.shape != (3,):
        raise ValueError(
            f"{name} must contain exactly three angles: (ths, thv, phi)."
        )
    if not np.all(np.isfinite(g)):
        raise ValueError(f"{name} must contain only finite angles.")
    g = g.copy()
    g.setflags(write=False)
    return g


def _bands_text(bands: np.ndarray) -> str:
    return ", ".join(f"{x:g}" for x in bands)


def assess_applicability(
    wl: object,
    source_geometry: object,
    target_geometry: object | None = None,
    tol_nm: float = BAND_TOLERANCE_NM,
) -> Applicability:
    """Assess whether O25 and BH4 can be applied.

    An omitted target geometry defaults to ``(0, 0, 0)``. O25 requires its
    four bands. BH4 additionally requires all first 12 OLCI bands and target
    geometry ``(0, 0, 0)``.

    Geometry domain limits are intentionally not checked here; this layer only
    validates the three-angle representation and the BH4 target restriction.
    """
    g0 = _geometry(source_geometry, "source_geometry")
    defaulted = target_geometry is None
    g1 = _geometry(
        DEFAULT_TARGET_GEOMETRY if defaulted else target_geometry,
        "target_geometry",
    )

    o25 = match_o25_bands(wl, tol_nm)
    bh4 = match_bh4_bands(wl, tol_nm)
    o25_ok = o25.complete
    target_ok = bool(np.allclose(g1, DEFAULT_TARGET_GEOMETRY, rtol=0.0,
                                 atol=_TARGET_ATOL))
    bh4_ok = o25_ok and bh4.complete and target_ok

    if o25_ok:
        o25_status = "available"
        o25_message = "O25 can be applied."
    else:
        o25_status = "missing_o25_bands"
        o25_message = (
            "O25 cannot be applied; missing required bands near "
            f"{_bands_text(o25.missing_nm)} nm (tolerance +/-{tol_nm:g} nm)."
        )

    if not o25_ok:
        bh4_status = "o25_unavailable"
        bh4_message = "BH4 cannot be applied because O25 is unavailable."
    elif not target_ok:
        bh4_status = "unsupported_target_geometry"
        bh4_message = (
            "BH4 is unavailable because its current target geometry must be "
            "(0, 0, 0). O25 can still correct to the requested target."
        )
    elif not bh4.complete:
        bh4_status = "missing_bh4_bands"
        bh4_message = (
            "BH4 is unavailable; missing required bands near "
            f"{_bands_text(bh4.missing_nm)} nm (tolerance +/-{tol_nm:g} nm). "
            "O25 can still be applied."
        )
    else:
        bh4_status = "available"
        bh4_message = "BH4 can be applied."

    return Applicability(
        source_geometry=g0,
        target_geometry=g1,
        target_was_defaulted=defaulted,
        o25_bands=o25,
        bh4_bands=bh4,
        o25_available=o25_ok,
        bh4_available=bh4_ok,
        o25_status=o25_status,
        bh4_status=bh4_status,
        o25_message=o25_message,
        bh4_message=bh4_message,
    )
