import numpy as np
import pytest

from o25._applicability import assess_applicability
from o25.bands import BH4_BANDS_NM

G0 = (30, 20, 90)


def test_omitted_target_defaults_to_zero_and_allows_bh4():
    a = assess_applicability(BH4_BANDS_NM, G0)
    np.testing.assert_array_equal(a.target_geometry, [0, 0, 0])
    assert a.target_was_defaulted
    assert a.o25_available
    assert a.bh4_available
    assert a.o25_status == "available"
    assert a.bh4_status == "available"


def test_explicit_zero_target_allows_bh4():
    a = assess_applicability(BH4_BANDS_NM, G0, (0, 0, 0))
    assert not a.target_was_defaulted
    assert a.bh4_available


def test_four_o25_bands_allow_o25_but_not_bh4():
    a = assess_applicability([443, 490, 560, 665], G0)
    assert a.o25_available
    assert not a.bh4_available
    assert a.bh4_status == "missing_bh4_bands"
    np.testing.assert_array_equal(
        a.bh4_bands.missing_nm,
        [400, 412, 510, 620, 673, 681, 709, 753],
    )
    assert "O25 can still be applied" in a.bh4_message


def test_nonzero_target_allows_o25_but_not_bh4():
    a = assess_applicability(BH4_BANDS_NM, G0, (40, 10, 120))
    assert a.o25_available
    assert not a.bh4_available
    assert a.bh4_status == "unsupported_target_geometry"
    assert "O25 can still correct" in a.bh4_message


def test_missing_o25_band_blocks_both_models():
    wl = [400, 412, 443, 490, 510, 560, 620, 673, 681, 709, 753]
    a = assess_applicability(wl, G0)
    assert not a.o25_available
    assert not a.bh4_available
    assert a.o25_status == "missing_o25_bands"
    assert a.bh4_status == "o25_unavailable"
    np.testing.assert_array_equal(a.o25_bands.missing_nm, [665])


def test_tolerance_is_used_by_both_models():
    wl = BH4_BANDS_NM + np.array([5, -5, 5, -5, 5, -5, 5, -5, 5, -5, 5, -5])
    a = assess_applicability(wl, G0)
    assert a.o25_available
    assert a.bh4_available


def test_custom_tolerance_is_respected():
    wl = BH4_BANDS_NM + 0.5
    assert assess_applicability(wl, G0, tol_nm=0.5).bh4_available
    assert not assess_applicability(wl, G0, tol_nm=0.49).o25_available


def test_target_numerically_zero_within_roundoff_allows_bh4():
    a = assess_applicability(BH4_BANDS_NM, G0, (1e-13, 0, 0))
    assert a.bh4_available


def test_target_beyond_roundoff_is_not_zero_target():
    a = assess_applicability(BH4_BANDS_NM, G0, (1e-8, 0, 0))
    assert not a.bh4_available
    assert a.bh4_status == "unsupported_target_geometry"


@pytest.mark.parametrize("g", [(1, 2), (1, 2, 3, 4), [[1, 2, 3]]])
def test_source_geometry_requires_three_vector(g):
    with pytest.raises(ValueError, match="exactly three"):
        assess_applicability(BH4_BANDS_NM, g)


@pytest.mark.parametrize("g", [(1, np.nan, 3), (1, np.inf, 3)])
def test_geometry_requires_finite_values(g):
    with pytest.raises(ValueError, match="finite"):
        assess_applicability(BH4_BANDS_NM, g)


def test_geometry_inputs_are_not_modified():
    g0 = np.array([30.0, 20.0, 90.0])
    g1 = np.array([0.0, 0.0, 0.0])
    assess_applicability(BH4_BANDS_NM, g0, g1)
    np.testing.assert_array_equal(g0, [30, 20, 90])
    np.testing.assert_array_equal(g1, [0, 0, 0])
