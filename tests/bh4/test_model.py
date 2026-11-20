from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat, savemat

import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4.model import (
    BH4ModelError,
    EXPECTED_PROBABILITIES,
    EXPECTED_WAVELENGTHS_NM,
    MODEL_FILE,
    load_model,
)


def test_packaged_model_loads_in_double_precision():
    m = load_model()
    assert m.selected_K == 4
    assert m.geometries.shape == (744, 3)
    assert m.absolute_relative_error_quantiles.shape == (4, 744, 12, 9)
    assert m.class_geometry_support.shape == (4, 744)
    assert m.classifier.centroids.shape == (4, 3)
    np.testing.assert_array_equal(m.wavelengths_nm, EXPECTED_WAVELENGTHS_NM)
    np.testing.assert_array_equal(m.required_probabilities, EXPECTED_PROBABILITIES)
    for a in (
        m.geometries, m.wavelengths_nm, m.levels, m.required_probabilities,
        m.absolute_relative_error_quantiles, m.class_geometry_support,
        m.classifier.feature_mean, m.classifier.feature_std,
        m.classifier.centroids,
    ):
        assert a.dtype == np.float64
        assert not a.flags.writeable


def test_packaged_model_is_found_outside_repository_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m = load_model()
    assert Path(m.source).name == MODEL_FILE
    assert m.version == "BH4-O25-operational-full744-working-1.0.1"


def test_support_and_quantile_contracts():
    m = load_model()
    np.testing.assert_array_equal(m.class_geometry_support.sum(axis=0), 5000)
    assert np.all(m.absolute_relative_error_quantiles >= 0)
    assert np.all(np.diff(m.absolute_relative_error_quantiles, axis=3) >= 0)
    assert m.quantile_storage_class == "single"
    assert m.runtime_precision == "double"
    assert m.interpolation_order == ("canonical RAA", "VZA", "SZA")


def test_arrays_cannot_be_modified():
    m = load_model()
    with pytest.raises(ValueError):
        m.wavelengths_nm[0] = -1
    with pytest.raises(ValueError):
        m.absolute_relative_error_quantiles[0, 0, 0, 0] = -1


def raw_packaged_model():
    m = loadmat(
        Path(__file__).parents[2] / "o25" / "data" / "bh4" / MODEL_FILE,
        simplify_cells=True,
    )["model"]
    return deepcopy(m)


def write_model(tmp_path, raw):
    path = tmp_path / "candidate.mat"
    savemat(path, {"model": raw}, do_compression=True, long_field_names=True)
    return path


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda x: x.pop("geometries"), "missing required field"),
        (lambda x: x.__setitem__("selected_K", 3), "selected_K must be 4"),
        (lambda x: x.__setitem__("geometries", x["geometries"][:-1]), r"expected \(744, 3\)"),
        (lambda x: x.__setitem__("wavelengths_nm", np.arange(12)), "wavelengths are incompatible"),
        (lambda x: x.__setitem__("required_probabilities", np.linspace(0, 1, 9)), "probabilities are incompatible"),
        (lambda x: x.__setitem__("class_geometry_support", np.zeros((4, 744))), "sum to 5000"),
    ],
)
def test_incompatible_models_are_rejected(tmp_path, mutation, message):
    raw = raw_packaged_model()
    mutation(raw)
    with pytest.raises(BH4ModelError, match=message):
        load_model(write_model(tmp_path, raw))


