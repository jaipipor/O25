import inspect
import numpy as np
import o25
from o25._core.coefficients import AngularCoefficients
from o25._core.correction import correct_rrs
from o25._core.iop import WaterOptics
from o25.model import O25Model, default_model


def test_public_frontend_uses_cached_default_model():
    assert default_model() is default_model()
    r = o25.correct([443, 490, 560, 665], np.full(4, .005), (30, 20, 90))
    assert r.Rrs.shape == (4,)


def test_model_owns_immutable_scientific_resources():
    m = O25Model()
    assert isinstance(m.coefficients, AngularCoefficients)
    assert isinstance(m.water, WaterOptics)
    assert not m.coefficients.values.flags.writeable
    assert not m.water.wavelength_nm.flags.writeable


def test_core_no_longer_contains_monolithic_o25_hyp():
    import o25._core.correction as module
    assert not hasattr(module, "O25_hyp")
    assert callable(correct_rrs)


def test_compatibility_wrapper_calls_class_based_model():
    source = inspect.getsource(o25.O25_hyp)
    assert "default_model().correct" in source


def test_normal_runtime_does_not_import_procedural_reference():
    """A clean O25 process must not load the procedural migration reference."""
    import subprocess
    import sys

    code = """
import sys
import o25

o25.correct(
    [443, 490, 560, 665],
    [0.004, 0.005, 0.006, 0.003],
    (30, 20, 120),
    (0, 0, 0),
)

assert "tests.reference.procedural_o25" not in sys.modules
assert "tests.reference.procedural_iop" not in sys.modules
assert "tests.reference.procedural_coefficients" not in sys.modules
"""

    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
    )
