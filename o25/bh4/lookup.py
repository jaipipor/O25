"""Exact-node lookup in the frozen Full-744 BH4 uncertainty table."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import BH4Model, load_model

GEOMETRY_TOLERANCE_DEG = 1e-10


class GeometryNotFoundError(ValueError):
    """Requested geometry is not an exact node of the frozen table."""


@dataclass(frozen=True)
class ExactLookupResult:
    """Relative-error quantiles and support at one stored geometry node."""

    class_id: int
    geometry: np.ndarray
    geometry_index: int
    wavelengths_nm: np.ndarray
    probabilities: np.ndarray
    quantiles: np.ndarray
    support: int
    geometry_mode: str = "exact_node"


def _readonly(a, dtype=np.float64):
    a = np.array(a, dtype=dtype, copy=True)
    a.setflags(write=False)
    return a


def _class_id(k) -> int:
    try:
        x = float(k)
    except (TypeError, ValueError) as exc:
        raise ValueError("class_id must be an integer from 1 to 4.") from exc
    if not np.isfinite(x) or not x.is_integer() or int(x) not in (1, 2, 3, 4):
        raise ValueError("class_id must be an integer from 1 to 4.")
    return int(x)


def _geometry(g) -> np.ndarray:
    try:
        g = np.asarray(g, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("geometry must contain three numeric angles: (SZA, VZA, RAA).") from exc
    if g.shape != (3,):
        raise ValueError("geometry must contain exactly three angles: (SZA, VZA, RAA).")
    if not np.all(np.isfinite(g)):
        raise ValueError("geometry must contain only finite angles.")
    return g


def canonical_geometry(g, tol_deg=GEOMETRY_TOLERANCE_DEG) -> np.ndarray:
    """Apply the MATLAB geometry convention before exact-node matching."""
    g = _geometry(g).copy()
    try:
        tol = float(tol_deg)
    except (TypeError, ValueError) as exc:
        raise ValueError("tol_deg must be finite and non-negative.") from exc
    if not np.isfinite(tol) or tol < 0:
        raise ValueError("tol_deg must be finite and non-negative.")

    # MATLAB: acosd(cosd(RAA)), expressed robustly without trig round-off.
    g[2] = abs((g[2] + 180.0) % 360.0 - 180.0)
    if abs(g[0]) <= tol or abs(g[1]) <= tol:
        g[2] = 0.0
    return _readonly(g)


def exact_node_lookup(
    class_id,
    geometry,
    model: BH4Model | None = None,
    tol_deg=GEOMETRY_TOLERANCE_DEG,
) -> ExactLookupResult:
    """Return the frozen 9-by-12 quantile table at an exact geometry node.

    Class identifiers follow MATLAB (1 to 4). Geometry follows (SZA, VZA,
    RAA). RAA is canonicalized to [0, 180], and is set to zero when SZA or
    VZA is zero. No interpolation is performed.
    """
    k = _class_id(class_id)
    if model is None:
        model = load_model()
    if not isinstance(model, BH4Model):
        raise TypeError("model must be a BH4Model.")

    g = canonical_geometry(geometry, tol_deg)
    tol = float(tol_deg)
    delta = np.max(np.abs(model.geometries - g), axis=1)
    matches = np.flatnonzero(delta <= tol)
    if matches.size == 0:
        raise GeometryNotFoundError(
            "geometry is not an exact Full-744 node after canonicalization: "
            f"({g[0]:g}, {g[1]:g}, {g[2]:g})."
        )
    if matches.size != 1:
        raise RuntimeError("Frozen BH4 model contains duplicate geometry nodes.")

    gi = int(matches[0])
    # Stored order is class, geometry, wavelength, probability. MATLAB's
    # geometry routine returns probability by wavelength.
    q = np.asarray(
        model.absolute_relative_error_quantiles[k - 1, gi], dtype=np.float64
    ).T
    if q.shape != (9, 12):
        raise RuntimeError(f"Internal BH4 quantile shape is {q.shape}; expected (9, 12).")
    if not np.all(np.isfinite(q)) or np.any(q < 0) or np.any(np.diff(q, axis=0) < 0):
        raise RuntimeError("Frozen BH4 quantiles violate their numerical contract.")

    support = model.class_geometry_support[k - 1, gi]
    if support < 0 or support != np.round(support):
        raise RuntimeError("Frozen BH4 support is not a non-negative integer.")

    return ExactLookupResult(
        class_id=k,
        geometry=_readonly(model.geometries[gi]),
        geometry_index=gi,
        wavelengths_nm=_readonly(model.wavelengths_nm),
        probabilities=_readonly(model.required_probabilities),
        quantiles=_readonly(q),
        support=int(support),
    )
