"""Regression protection for the Python O25 implementation as received.

The fixture was generated before the repository rebuild. These tests do not
claim MATLAB equivalence; they detect unintended changes to current Python
behaviour while the package is restructured.
"""
from pathlib import Path

import numpy as np

from o25.O25_hyp import O25_hyp


FIXTURE = Path(__file__).parent / "data" / "legacy_o25_reference.npz"


def load_reference():
    with np.load(FIXTURE) as ref:
        return {name: ref[name].copy() for name in ref.files}


def test_legacy_reference_is_reproduced():
    ref = load_reference()

    a, bb, rrs_n = O25_hyp(ref["wl"], ref["rrs"], ref["g0"], ref["g1"])

    np.testing.assert_allclose(a, ref["a"], rtol=1e-12, atol=0.0)
    np.testing.assert_allclose(bb, ref["bb"], rtol=1e-12, atol=0.0)
    np.testing.assert_allclose(rrs_n, ref["rrs_n"], rtol=1e-12, atol=0.0)


def test_legacy_output_shapes_follow_input_spectrum():
    ref = load_reference()

    a, bb, rrs_n = O25_hyp(ref["wl"], ref["rrs"], ref["g0"], ref["g1"])

    assert a.shape == ref["wl"].shape
    assert bb.shape == ref["wl"].shape
    assert rrs_n.shape == ref["wl"].shape


def test_legacy_call_does_not_modify_inputs():
    ref = load_reference()
    wl = ref["wl"].copy()
    rrs = ref["rrs"].copy()
    g0 = ref["g0"].copy()
    g1 = ref["g1"].copy()

    O25_hyp(wl, rrs, g0, g1)

    np.testing.assert_array_equal(wl, ref["wl"])
    np.testing.assert_array_equal(rrs, ref["rrs"])
    np.testing.assert_array_equal(g0, ref["g0"])
    np.testing.assert_array_equal(g1, ref["g1"])
