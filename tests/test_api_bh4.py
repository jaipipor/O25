import numpy as np
import pytest
import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4 import uncertainty_from_rrs

G0=(30,20,120)
R=np.array([.0030,.0034,.0048,.0068,.0075,.0086,.0072,.0051,.0048,.0045,.0036,.0022])

def test_default_target_integrates_bh4_at_native_bands():
    r=o25.correct(BH4_BANDS_NM,R,G0)
    b=uncertainty_from_rrs(R,BH4_BANDS_NM,G0)
    j=np.flatnonzero(b.probabilities==.68).item()
    assert r.has_uncertainty and r.uncertainty_status=='available_native_olci'
    assert r.k==4 and r.p==.68 and r.bh4 is not None
    np.testing.assert_array_equal(r.uncertainty_mask,np.ones(12,dtype=bool))
    np.testing.assert_array_equal(r.u_rel,b.quantiles[0,:,j])
    np.testing.assert_array_equal(r.u,r.u_rel*np.abs(r.Rrs))

def test_hyperspectral_non_olci_uncertainties_are_nan():
    wl=np.r_[350.,BH4_BANDS_NM,800.]
    x=np.r_[.002,R,.001]
    r=o25.correct(wl,x,G0)
    assert r.Rrs.shape==wl.shape and r.u.shape==wl.shape
    assert r.uncertainty_mask.sum()==12
    assert np.isnan(r.u_rel[[0,-1]]).all() and np.isnan(r.u[[0,-1]]).all()
    assert np.isfinite(r.u_rel[r.uncertainty_mask]).all()
    assert 'spectral interpolation is not applied' in r.uncertainty_message

def test_alternative_stored_probability_is_selectable():
    r=o25.correct(BH4_BANDS_NM,R,G0,p=.95)
    assert r.p==.95
    assert np.all(r.u_rel>=0)
    with pytest.raises(ValueError,match='stored BH4 probabilities'):
        o25.correct(BH4_BANDS_NM,R,G0,p=.7)

def test_arbitrary_target_still_runs_o25_without_uncertainty():
    r=o25.correct(BH4_BANDS_NM,R,G0,(40,10,120))
    assert not r.has_uncertainty and r.u is None and r.k is None
    assert r.uncertainty_status=='unsupported_target_geometry'

def test_missing_bh4_bands_still_runs_o25():
    wl=np.array([443.,490.,560.,665.]); r=o25.correct(wl,np.full(4,.005),G0)
    assert not r.has_uncertainty and r.uncertainty_status=='missing_bh4_bands'

def test_bh4_source_geometry_outside_domain_does_not_block_o25():
    r=o25.correct(BH4_BANDS_NM,R,(85,20,120))
    assert not r.has_uncertainty
    assert r.uncertainty_status=='bh4_input_outside_domain'
    assert 'outside' in r.uncertainty_message

