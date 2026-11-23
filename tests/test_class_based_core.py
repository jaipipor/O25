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
