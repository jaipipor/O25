import numpy as np
import pytest

import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4 import (
    GeometryNotFoundError,
    canonical_geometry,
    exact_node_lookup,
    load_model,
)


def test_first_node_matches_frozen_table_and_support():
    m = load_model()
    r = exact_node_lookup(1, (0, 0, 137), m)
    assert r.geometry_index == 0
    np.testing.assert_array_equal(r.geometry, [0, 0, 0])
    assert r.geometry_mode == "exact_node"
    assert r.support == 2557
    np.testing.assert_array_equal(r.quantiles, m.absolute_relative_error_quantiles[0, 0].T)


def test_arbitrary_exact_node_matches_all_classes():
    m = load_model()
    gi = 100
    for k in range(1, 5):
        r = exact_node_lookup(k, m.geometries[gi], m)
        assert r.geometry_index == gi
        assert r.support == int(m.class_geometry_support[k - 1, gi])
        np.testing.assert_array_equal(
            r.quantiles,
            m.absolute_relative_error_quantiles[k - 1, gi].T,
        )


def test_all_2976_class_geometry_combinations_match_the_frozen_table():
    m = load_model()
    for gi, g in enumerate(m.geometries):
        for k in range(1, 5):
            r = exact_node_lookup(k, g, m)
            assert r.geometry_index == gi
            assert r.support == int(m.class_geometry_support[k - 1, gi])
            np.testing.assert_array_equal(
                r.quantiles,
                m.absolute_relative_error_quantiles[k - 1, gi].T,
            )


def test_output_orientation_is_probability_by_wavelength():
    r = exact_node_lookup(4, (80, 70, 180))
    assert r.quantiles.shape == (9, 12)
    np.testing.assert_array_equal(
        r.probabilities,
        [0.025, 0.05, 0.16, 0.5, 0.68, 0.84, 0.9, 0.95, 0.975],
    )
    np.testing.assert_array_equal(r.wavelengths_nm, BH4_BANDS_NM)
    np.testing.assert_allclose(
        r.quantiles[:, 11],
        [0.28949445, 0.38915157, 0.62188387, 0.81079561, 0.87934649,
         0.96466964, 1.00678158, 1.07362390, 1.19949615],
        rtol=3e-8,
    )


def test_raa_is_canonicalized_like_matlab():
    np.testing.assert_array_equal(canonical_geometry((30, 20, -120)), [30, 20, 120])
    np.testing.assert_array_equal(canonical_geometry((30, 20, 240)), [30, 20, 120])
    a = exact_node_lookup(2, (30, 20, -120))
    b = exact_node_lookup(2, (30, 20, 120))
    assert a.geometry_index == b.geometry_index
    np.testing.assert_array_equal(a.quantiles, b.quantiles)


def test_raa_is_irrelevant_when_sza_or_vza_is_zero():
    assert exact_node_lookup(1, (30, 0, 173)).geometry_index == exact_node_lookup(1, (30, 0, 0)).geometry_index
    assert exact_node_lookup(1, (0, 60, 173)).geometry_index == exact_node_lookup(1, (0, 60, 0)).geometry_index


def test_roundoff_tolerance_accepts_node_but_not_interpolation_point():
    a = exact_node_lookup(3, (30 + 5e-11, 20, 120))
    b = exact_node_lookup(3, (30, 20, 120))
    assert a.geometry_index == b.geometry_index
    with pytest.raises(GeometryNotFoundError, match="not an exact"):
        exact_node_lookup(3, (30.001, 20, 120))


@pytest.mark.parametrize("k", [0, 5, 1.5, np.nan, "blue"])
def test_invalid_class_is_rejected(k):
    with pytest.raises(ValueError, match="integer from 1 to 4"):
        exact_node_lookup(k, (0, 0, 0))


@pytest.mark.parametrize(
    "g, message",
    [
        ((1, 2), "exactly three"),
        ((1, 2, 3, 4), "exactly three"),
        ((1, np.nan, 3), "finite"),
        ((1, np.inf, 3), "finite"),
        ((63.24, 45, 120), "not an exact"),
    ],
)
def test_invalid_or_non_node_geometry_is_rejected(g, message):
    error = GeometryNotFoundError if "not an exact" in message else ValueError
    with pytest.raises(error, match=message):
        exact_node_lookup(1, g)


def test_outputs_are_double_and_read_only():
    r = exact_node_lookup(4, (50, 40, 15))
    for a in (r.geometry, r.wavelengths_nm, r.probabilities, r.quantiles):
        assert a.dtype == np.float64
        assert not a.flags.writeable


