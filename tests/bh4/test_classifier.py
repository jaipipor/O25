import numpy as np
import pytest

import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4 import assign_class, features_from_rrs, load_model
from o25.bh4.model import BH4Classifier


def test_reference_spectra_assign_valid_frozen_classes():
    Rrs = np.array([
        [.0030, .0034, .0048, .0068, .0075, .0086, .0072, .0051, .0048, .0045, .0036, .0022],
        [.0100, .0096, .0084, .0065, .0058, .0044, .0031, .0022, .0020, .0018, .0014, .0009],
    ])
    f = features_from_rrs(Rrs, BH4_BANDS_NM)
    r = assign_class(f.values, load_model())
    np.testing.assert_array_equal(r.class_id, [4, 3])
    np.testing.assert_allclose(
        r.top_two_margin,
        [5.882312989689186, 0.9770420437868781],
        rtol=2e-13,
    )


def test_each_centroid_assigns_its_own_class():
    c = load_model().classifier
    # Invert standardization and Box-Cox to obtain raw feature coordinates.
    t = c.centroids * c.feature_std + c.feature_mean
    j = c.boxcox_feature_index - 1
    lam = c.boxcox_lambda
    t[:, j] = np.exp(t[:, j]) if abs(lam) < 1e-12 else (lam * t[:, j] + 1) ** (1 / lam)
    r = assign_class(t, c)
    np.testing.assert_array_equal(r.class_id, [1, 2, 3, 4])
    np.testing.assert_allclose(np.min(r.centroid_squared_distance, axis=1), 0, atol=2e-29)


def test_tie_uses_first_class_as_matlab_does():
    c = BH4Classifier(
        boxcox_feature_index=2,
        boxcox_lambda=0.0,
        feature_mean=np.zeros(3),
        feature_std=np.ones(3),
        centroids=np.array([[-1., 0, 0], [1., 0, 0], [10., 0, 0], [20., 0, 0]]),
    )
    r = assign_class([0, 1, 0], c)
    assert r.class_id.item() == 1
    assert r.top_two_margin.item() == 0


@pytest.mark.parametrize(
    "features, message",
    [
        ([1, 2], "shape"),
        ([[1, 2, 3, 4]], "shape"),
        ([1, np.nan, 3], "finite"),
        ([1, 0, 3], "strictly positive"),
    ],
)
def test_invalid_features_are_rejected(features, message):
    with pytest.raises(ValueError, match=message):
        assign_class(features)


def test_outputs_are_double_or_integer_and_read_only():
    r = assign_class([500, 1, .2])
    assert r.class_id.dtype == np.int64
    assert not r.class_id.flags.writeable
    for a in (r.standardized_features, r.centroid_squared_distance, r.top_two_margin):
        assert a.dtype == np.float64
        assert not a.flags.writeable


def test_public_frontend_is_still_not_connected():
    r = o25.correct(BH4_BANDS_NM, np.full(12, .005), (30, 20, 90))
    assert r.uncertainty_status == "not_implemented"
    assert r.u is None and r.u_rel is None and r.k is None
