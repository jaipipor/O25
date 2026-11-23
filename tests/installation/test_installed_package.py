import numpy as np
import o25
from o25.bands import BH4_BANDS_NM
from o25.bh4 import load_model

def test_installed_resources_work_outside_repository(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert load_model().geometries.shape==(744,3)
    R=np.array([.0030,.0034,.0048,.0068,.0075,.0086,.0072,.0051,.0048,.0045,.0036,.0022])
    r=o25.correct(BH4_BANDS_NM,R,(30,20,120))
    assert r.has_uncertainty and np.isfinite(r.u).all()
