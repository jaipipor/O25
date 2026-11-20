import numpy as np
import pytest

import o25
from o25.O25_hyp import O25_hyp
from o25.bands import BH4_BANDS_NM

G0 = (30, 20, 90)
RRS = np.full(BH4_BANDS_NM.size, 0.005)


def test_correct_is_public():
    assert callable(o25.correct)


def test_default_target_and_named_outputs_match_legacy_function():
    r = o25.correct(BH4_BANDS_NM, RRS, G0)
    a, bb, Rrs_n = O25_hyp(BH4_BANDS_NM, RRS, G0, (0, 0, 0))

    np.testing.assert_array_equal(r.g1, [0, 0, 0])
    np.testing.assert_allclose(r.a, a, rtol=0, atol=0)
    np.testing.assert_allclose(r.bb, bb, rtol=0, atol=0)
    np.testing.assert_allclose(r.Rrs, Rrs_n, rtol=0, atol=0)
    assert r.uncertainty_status == "not_implemented"
    assert not r.has_uncertainty
    assert r.u is None
    assert r.u_rel is None
    assert r.k is None


def test_arbitrary_target_runs_o25_without_bh4():
    r = o25.correct(BH4_BANDS_NM, RRS, G0, (40, 10, 120))
    assert r.uncertainty_status == "unsupported_target_geometry"
    assert not r.has_uncertainty


def test_minimum_o25_bands_run_without_bh4():
    wl = np.array([443.0, 490.0, 560.0, 665.0])
    r = o25.correct(wl, np.full(wl.size, 0.005), G0)
    assert r.uncertainty_status == "missing_bh4_bands"
    assert r.Rrs.shape == wl.shape


def test_missing_o25_bands_raise_before_the_numerical_model_runs():
    with pytest.raises(ValueError, match="O25 cannot be applied"):
        o25.correct([443, 490, 560], np.full(3, 0.005), G0)


def test_wavelength_and_rrs_lengths_must_match():
    with pytest.raises(ValueError, match="same length"):
        o25.correct([443, 490, 560, 665], np.full(3, 0.005), G0)


@pytest.mark.parametrize(
    "wl, Rrs, message",
    [
        ([[443, 490, 560, 665]], np.full(4, 0.005), "wl"),
        ([443, 490, 560, 665], [0.005, np.nan, 0.005, 0.005], "Rrs"),
        ([443, 490, 560, 665], [[0.005] * 4], "Rrs"),
    ],
)
def test_invalid_spectral_arrays_raise_clear_errors(wl, Rrs, message):
    with pytest.raises(ValueError, match=message):
        o25.correct(wl, Rrs, G0)


def test_inputs_are_not_modified():
    wl = BH4_BANDS_NM.copy()
    Rrs = RRS.copy()
    g0 = np.array(G0, dtype=float)
    o25.correct(wl, Rrs, g0)
    np.testing.assert_array_equal(wl, BH4_BANDS_NM)
    np.testing.assert_array_equal(Rrs, RRS)
    np.testing.assert_array_equal(g0, G0)
