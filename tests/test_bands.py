import numpy as np
import pytest
from o25.bands import (BAND_TOLERANCE_NM, BH4_BANDS_NM, O25_BANDS_NM,
                       match_bands, match_bh4_bands, match_o25_bands)

def test_frozen_contract():
    assert BAND_TOLERANCE_NM == 5.0
    np.testing.assert_array_equal(O25_BANDS_NM, [443, 490, 560, 665])
    np.testing.assert_array_equal(BH4_BANDS_NM,
        [400, 412, 443, 490, 510, 560, 620, 665, 673, 681, 709, 753])

def test_exact_o25_match():
    m = match_o25_bands([443, 490, 560, 665])
    assert m.complete
    np.testing.assert_array_equal(m.indices, [0, 1, 2, 3])
    np.testing.assert_array_equal(m.delta_nm, [0, 0, 0, 0])

@pytest.mark.parametrize("x", [438.0, 448.0])
def test_boundaries_inclusive(x):
    assert match_bands([x], [443]).complete

@pytest.mark.parametrize("x", [437.999, 448.001])
def test_outside_rejected(x):
    m = match_bands([x], [443])
    assert not m.complete
    np.testing.assert_array_equal(m.missing_nm, [443])

def test_closest_independent_of_order():
    assert match_bands([445, 442, 439], [443]).matched_nm[0] == 442
    assert match_bands([439, 442, 445], [443]).matched_nm[0] == 442

def test_one_observation_cannot_fill_two_bands():
    m = match_bands([669], [665, 673])
    assert np.count_nonzero(m.indices >= 0) == 1

def test_global_assignment_maximizes_matches():
    m = match_bands([668, 661], [665, 673])
    assert m.complete
    np.testing.assert_array_equal(m.matched_nm, [661, 668])

def test_tie_prefers_lower_input_index():
    m = match_bands([441, 445], [443])
    assert m.indices[0] == 0

def test_missing_reported_in_required_order():
    m = match_o25_bands([443, 561])
    np.testing.assert_array_equal(m.missing_nm, [490, 665])
    assert np.isnan(m.matched_nm[1])

def test_all_bh4_bands_with_offsets():
    offset = np.array([.1, -.2, .3, -.4, .5, -.6, .7, -.8, .9, -1, 1.1, -1.2])
    m = match_bh4_bands((BH4_BANDS_NM + offset)[::-1])
    assert m.complete
    assert np.unique(m.indices).size == 12

@pytest.mark.parametrize("wl,msg", [
    ([443, 443], "duplicate"), ([443, np.nan], "finite"),
    ([[443, 490]], "one-dimensional"), ([], "must not be empty"),
    (["blue", "green"], "numeric")])
def test_invalid_wavelengths(wl, msg):
    with pytest.raises(ValueError, match=msg):
        match_o25_bands(wl)

@pytest.mark.parametrize("tol", [-1, np.nan, np.inf, "bad"])
def test_invalid_tolerance(tol):
    with pytest.raises(ValueError, match="tol_nm"):
        match_o25_bands([443, 490, 560, 665], tol)
