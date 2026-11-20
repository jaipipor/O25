import numpy as np
import pytest

from o25.bands import BH4_BANDS_NM
from o25.bh4 import features_from_rrs


def reference_spectra():
    wl = BH4_BANDS_NM.copy()
    r1 = np.array([.0030, .0034, .0048, .0068, .0075, .0086,
                   .0072, .0051, .0048, .0045, .0036, .0022])
    r2 = np.array([.0100, .0096, .0084, .0065, .0058, .0044,
                   .0031, .0022, .0020, .0018, .0014, .0009])
    return wl, np.vstack((r1, r2))


def test_frozen_matlab_formula_reference_values():
    wl, Rrs = reference_spectra()
    r = features_from_rrs(Rrs, wl)
    expected = np.array([
        [5.4624400995544852e2, 1.5031500000000000e0, 2.554744525547445e-1],
        [4.7741984330500776e2, 1.0952999999999999e0, 3.333333333333333e-1],
    ])
    expected_discrete = np.array([5.513238189591473e2, 4.801000822552518e2])
    np.testing.assert_allclose(r.values, expected, rtol=2e-14, atol=2e-14)
    np.testing.assert_allclose(r.avw_discrete_nm, expected_discrete, rtol=2e-14)


def test_vector_input_returns_one_row_and_matches_offset_bands():
    wl, Rrs = reference_spectra()
    offset = np.array([1, -1, 2, -2, 3, -3, 4, -4, 5, -5, .5, -.5])
    r = features_from_rrs(Rrs[0], wl + offset)
    assert r.values.shape == (1, 3)
    assert np.unique(r.selected_indices).size == 12
    assert np.all(np.abs((wl + offset)[r.selected_indices] - wl) <= 5.0)


def test_extra_bands_and_reordered_input_are_supported():
    wl, Rrs = reference_spectra()
    wl2 = np.r_[800, wl[::-1], 350]
    x = np.r_[.0005, Rrs[0, ::-1], .0004]
    a = features_from_rrs(Rrs[0], wl)
    b = features_from_rrs(x, wl2)
    np.testing.assert_allclose(a.values, b.values, rtol=0, atol=0)


@pytest.mark.parametrize(
    "Rrs, wl, message",
    [
        (np.ones(11), BH4_BANDS_NM, "spectral length"),
        (np.ones(12), BH4_BANDS_NM[:-1].tolist() + [800], "requires bands"),
        (np.r_[np.ones(11), 0], BH4_BANDS_NM, "strictly positive"),
        (np.r_[np.ones(11), np.nan], BH4_BANDS_NM, "finite"),
        (np.ones((1, 1, 12)), BH4_BANDS_NM, "one- or two-dimensional"),
    ],
)
def test_invalid_inputs_are_rejected(Rrs, wl, message):
    with pytest.raises(ValueError, match=message):
        features_from_rrs(Rrs, wl)


def test_outputs_are_double_and_read_only():
    wl, Rrs = reference_spectra()
    r = features_from_rrs(Rrs.astype(np.float32), wl)
    for a in (r.values, r.avw_discrete_nm, r.avw_corrected_nm):
        assert a.dtype == np.float64
        assert not a.flags.writeable
    assert r.selected_indices.dtype == np.int64
    assert not r.selected_indices.flags.writeable
