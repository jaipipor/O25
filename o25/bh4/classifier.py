"""Frozen four-class BH4 assignment ported from ``bh4_assign_class.m``."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import BH4Classifier, BH4Model, load_model


@dataclass(frozen=True)
class ClassResult:
    """Assigned class and classifier diagnostics for each spectrum."""

    class_id: np.ndarray
    standardized_features: np.ndarray
    centroid_squared_distance: np.ndarray
    top_two_margin: np.ndarray


def _readonly(a, dtype=np.float64):
    a = np.array(a, dtype=dtype, copy=True)
    a.setflags(write=False)
    return a


def assign_class(features, classifier: BH4Classifier | None = None) -> ClassResult:
    """Assign nearest frozen centroid; class identifiers are 1, 2, 3, or 4."""
    if classifier is None:
        classifier = load_model().classifier
    elif isinstance(classifier, BH4Model):
        classifier = classifier.classifier
    if not isinstance(classifier, BH4Classifier):
        raise TypeError("classifier must be a BH4Classifier or BH4Model.")

    try:
        x = np.asarray(features, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("features must contain numeric values.") from exc
    if x.ndim == 1:
        x = x.reshape(1, -1)
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError("features must have shape (3,) or (N, 3).")
    if not np.all(np.isfinite(x)):
        raise ValueError("features must contain only finite values.")

    t = x.copy()
    # MATLAB stores a one-based feature index; the Python model preserves it.
    j = classifier.boxcox_feature_index - 1
    v = t[:, j]
    if np.any(v <= 0):
        raise ValueError("The Box-Cox feature must be strictly positive.")
    lam = classifier.boxcox_lambda
    t[:, j] = np.log(v) if abs(lam) < 1e-12 else (v**lam - 1.0) / lam

    z = (t - classifier.feature_mean) / classifier.feature_std
    delta = z[:, None, :] - classifier.centroids[None, :, :]
    d2 = np.sum(delta * delta, axis=2)
    # np.argmin returns the first minimum, matching MATLAB's class-order tie rule.
    k = np.argmin(d2, axis=1).astype(np.int64) + 1
    ordered = np.sort(d2, axis=1)
    margin = ordered[:, 1] - ordered[:, 0]

    return ClassResult(
        class_id=_readonly(k, np.int64),
        standardized_features=_readonly(z),
        centroid_squared_distance=_readonly(d2),
        top_two_margin=_readonly(margin),
    )
