"""Read-only loader for the frozen BH4 Full-744 MATLAB model."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, fields
from importlib.resources import as_file, files
from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import loadmat

MODEL_FILE = "BH4_O25_operational_class_full744_direct_increment.mat"
EXPECTED_VERSION = "BH4-O25-operational-full744-working-1.0.1"
EXPECTED_SOURCE_VERSION = (
    "BH4-O25-corrected-AVW-full744-production-1.1-double-authoritative"
)
EXPECTED_WAVELENGTHS_NM = np.array(
    [400, 412, 443, 490, 510, 560, 620, 665, 673, 681, 709, 753],
    dtype=np.float64,
)
EXPECTED_PROBABILITIES = np.array(
    [0.025, 0.05, 0.16, 0.50, 0.68, 0.84, 0.90, 0.95, 0.975],
    dtype=np.float64,
)


class BH4ModelError(ValueError):
    """The MAT file is incomplete or incompatible with this BH4 release."""


@dataclass(frozen=True)
class BH4Classifier:
    boxcox_feature_index: int
    boxcox_lambda: float
    feature_mean: np.ndarray
    feature_std: np.ndarray
    centroids: np.ndarray


@dataclass(frozen=True)
class BH4Model:
    version: str
    source_production_version: str
    selected_K: int
    geometries: np.ndarray
    wavelengths_nm: np.ndarray
    levels: np.ndarray
    required_probabilities: np.ndarray
    absolute_relative_error_quantiles: np.ndarray
    class_geometry_support: np.ndarray
    classifier: BH4Classifier
    quantile_storage_class: str
    runtime_precision: str
    interpolation_method: str
    interpolation_order: tuple[str, str, str]
    source: str


def _fail(message: str) -> None:
    raise BH4ModelError(message)


def _required(mapping: dict[str, Any], name: str) -> Any:
    if name not in mapping:
        _fail(f'BH4 model is missing required field "{name}".')
    return mapping[name]


def _text(value: Any, name: str) -> str:
    a = np.asarray(value)
    if a.size != 1:
        _fail(f'BH4 field "{name}" must contain one text value.')
    return str(a.reshape(-1)[0])


def _scalar(value: Any, name: str) -> float:
    a = np.asarray(value)
    if a.size != 1 or not np.issubdtype(a.dtype, np.number):
        _fail(f'BH4 field "{name}" must contain one numeric value.')
    x = float(a.reshape(-1)[0])
    if not np.isfinite(x):
        _fail(f'BH4 field "{name}" must be finite.')
    return x


def _array(value: Any, name: str, shape: tuple[int, ...]) -> np.ndarray:
    try:
        a = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise BH4ModelError(f'BH4 field "{name}" must be numeric.') from exc
    if a.shape != shape:
        _fail(f'BH4 field "{name}" has shape {a.shape}; expected {shape}.')
    if not np.all(np.isfinite(a)):
        _fail(f'BH4 field "{name}" contains non-finite values.')
    a = np.array(a, dtype=np.float64, copy=True)
    a.setflags(write=False)
    return a


def _classifier(value: Any) -> BH4Classifier:
    if not isinstance(value, dict):
        _fail('BH4 field "classifier" must be a scalar MATLAB structure.')
    j = _scalar(_required(value, "boxcox_feature_index"), "classifier.boxcox_feature_index")
    if not j.is_integer() or int(j) not in (1, 2, 3):
        _fail("BH4 classifier Box-Cox feature index must be 1, 2, or 3.")
    lam = _scalar(_required(value, "boxcox_lambda"), "classifier.boxcox_lambda")
    mean = _array(_required(value, "feature_mean"), "classifier.feature_mean", (3,))
    std = _array(_required(value, "feature_std"), "classifier.feature_std", (3,))
    centroids = _array(_required(value, "centroids"), "classifier.centroids", (4, 3))
    if np.any(std <= 0):
        _fail("BH4 classifier feature standard deviations must be positive.")
    return BH4Classifier(int(j), lam, mean, std, centroids)


def _freeze_model(model: BH4Model) -> BH4Model:
    # Defensive assertion: every exposed NumPy array is immutable.
    for field in fields(model):
        value = getattr(model, field.name)
        if isinstance(value, np.ndarray) and value.flags.writeable:
            _fail(f'Internal error: field "{field.name}" is writeable.')
    return model


def _build(raw: dict[str, Any], source: str) -> BH4Model:
    version = _text(_required(raw, "version"), "version")
    source_version = _text(
        _required(raw, "source_production_version"), "source_production_version"
    )
    if version != EXPECTED_VERSION:
        _fail(f'Unsupported BH4 version "{version}"; expected "{EXPECTED_VERSION}".')
    if source_version != EXPECTED_SOURCE_VERSION:
        _fail("BH4 source-production version is incompatible with this loader.")

    k = _scalar(_required(raw, "selected_K"), "selected_K")
    if k != 4:
        _fail(f"BH4 selected_K must be 4; found {k:g}.")

    g = _array(_required(raw, "geometries"), "geometries", (744, 3))
    wl = _array(_required(raw, "wavelengths_nm"), "wavelengths_nm", (12,))
    levels = _array(_required(raw, "levels"), "levels", (3,))
    p = _array(
        _required(raw, "required_probabilities"), "required_probabilities", (9,)
    )
    q = _array(
        _required(raw, "absolute_relative_error_quantiles"),
        "absolute_relative_error_quantiles",
        (4, 744, 12, 9),
    )
    support = _array(
        _required(raw, "class_geometry_support"), "class_geometry_support", (4, 744)
    )

    if not np.array_equal(wl, EXPECTED_WAVELENGTHS_NM):
        _fail("BH4 wavelengths are incompatible with the frozen 12-band model.")
    if not np.array_equal(p, EXPECTED_PROBABILITIES):
        _fail("BH4 stored probabilities are incompatible with this loader.")
    if not np.array_equal(levels, [0.68, 0.90, 0.95]):
        _fail("BH4 confidence levels are incompatible with this loader.")
    if np.any(q < 0) or np.any(np.diff(q, axis=3) < 0):
        _fail("BH4 quantiles must be non-negative and nondecreasing.")
    if np.any(support < 0) or not np.all(support == np.round(support)):
        _fail("BH4 class-geometry support must contain non-negative integers.")
    if not np.all(np.sum(support, axis=0) == 5000):
        _fail("BH4 support must sum to 5000 cases at every geometry.")

    order_raw = np.asarray(_required(raw, "interpolation_order"), dtype=object).reshape(-1)
    order = tuple(str(x) for x in order_raw)
    if order != ("canonical RAA", "VZA", "SZA"):
        _fail("BH4 interpolation order is incompatible with this loader.")

    storage = _text(_required(raw, "quantile_storage_class"), "quantile_storage_class")
    runtime = _text(_required(raw, "runtime_precision"), "runtime_precision")
    if storage != "single" or runtime != "double":
        _fail("BH4 precision metadata is incompatible with this release.")

    return _freeze_model(BH4Model(
        version=version,
        source_production_version=source_version,
        selected_K=4,
        geometries=g,
        wavelengths_nm=wl,
        levels=levels,
        required_probabilities=p,
        absolute_relative_error_quantiles=q,
        class_geometry_support=support,
        classifier=_classifier(_required(raw, "classifier")),
        quantile_storage_class=storage,
        runtime_precision=runtime,
        interpolation_method=_text(
            _required(raw, "interpolation_method"), "interpolation_method"
        ),
        interpolation_order=order,
        source=source,
    ))


def load_model(path: str | PathLike[str] | None = None) -> BH4Model:
    """Load and validate the frozen model, converting all numerics to float64.

    With ``path=None``, the MAT file packaged under ``o25/data/bh4`` is used.
    The returned arrays are read-only. This function does not modify global
    state and is not connected to :func:`o25.correct` yet.
    """
    with ExitStack() as stack:
        if path is None:
            resource = files("o25").joinpath("data", "bh4", MODEL_FILE)
            model_path = stack.enter_context(as_file(resource))
        else:
            model_path = Path(path)
        if not model_path.is_file():
            raise FileNotFoundError(f"BH4 model file not found: {model_path}")
        try:
            loaded = loadmat(model_path, simplify_cells=True)
        except Exception as exc:
            raise BH4ModelError(f"Could not read BH4 MATLAB model: {model_path}") from exc
        raw = loaded.get("model")
        if not isinstance(raw, dict):
            _fail('MAT file must contain one scalar structure named "model".')
        return _build(raw, str(model_path))
