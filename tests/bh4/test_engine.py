import numpy as np
import pytest
import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4 import geometry_quantiles, load_model, uncertainty_from_rrs

R1=np.array([.0030,.0034,.0048,.0068,.0075,.0086,.0072,.0051,.0048,.0045,.0036,.0022])
R2=np.array([.0100,.0096,.0084,.0065,.0058,.0044,.0031,.0022,.0020,.0018,.0014,.0009])

def test_all_exact_nodes_remain_identical():
    m=load_model()
    for gi,g in enumerate(m.geometries):
        for k in range(1,5):
            r=geometry_quantiles(k,g,m)
            assert r.geometry_mode=='direct' and not r.interpolation_used
            np.testing.assert_array_equal(r.quantiles,m.absolute_relative_error_quantiles[k-1,gi].T)

def test_interpolated_reference_geometry_is_valid_and_reproducible():
    r=geometry_quantiles(4,(63.24,45,120))
    assert r.geometry_mode=='interpolated' and r.interpolation_used
    assert r.quantiles.shape==(9,12)
    assert np.all(r.quantiles>=0) and np.all(np.diff(r.quantiles,axis=0)>=0)
    np.testing.assert_allclose(r.quantiles[[0,4,8],[0,5,11]],
        [0.008942230065446654,0.1451429671086478,0.23429326621868762],rtol=2e-12)

def test_geometry_boundaries_and_degenerate_azimuths():
    for g in [(0,0,0),(80,70,180),(0,35,177),(65,0,-99)]:
        r=geometry_quantiles(1,g); assert np.all(np.isfinite(r.quantiles))

@pytest.mark.parametrize('g',[(80.001,20,30),(20,70.001,30)])
def test_out_of_domain_geometry_is_rejected(g):
    with pytest.raises(ValueError,match='outside'): geometry_quantiles(1,g)

def test_standalone_engine_single_and_batch():
    a=uncertainty_from_rrs(R1,BH4_BANDS_NM,(63.24,45,120))
    assert a.quantiles.shape==(1,12,9) and a.class_id.tolist()==[4]
    b=uncertainty_from_rrs(np.vstack((R1,R2)),BH4_BANDS_NM,[(30,20,120),(63.24,45,120)])
    assert b.quantiles.shape==(2,12,9) and b.class_id.tolist()==[4,3]
    assert b.geometry[0].geometry_mode=='direct' and b.geometry[1].geometry_mode=='interpolated'

def test_shared_geometry_is_broadcast_across_spectra():
    r=uncertainty_from_rrs(np.vstack((R1,R2)),BH4_BANDS_NM,(30,20,120))
    assert len(r.geometry)==2 and r.quantiles.dtype==np.float64
    assert not r.quantiles.flags.writeable

def test_geometry_batch_size_must_match():
    with pytest.raises(ValueError,match='matching Rrs'):
        uncertainty_from_rrs(np.vstack((R1,R2)),BH4_BANDS_NM,[(30,20,120)])

def test_public_frontend_remains_unconnected():
    r=o25.correct(BH4_BANDS_NM,np.full(12,.005),(30,20,90))
    assert r.uncertainty_status=='not_implemented' and r.u is None
