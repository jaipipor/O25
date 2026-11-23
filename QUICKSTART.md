# O25 quick start

## 1. Install

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install o25
```

## 2. Correct a spectrum

```python
import numpy as np
import o25

data = np.loadtxt("examples/data/example_spectrum.csv", delimiter=",", skiprows=1)
wl, Rrs = data[:, 0], data[:, 1]
r = o25.correct(wl, Rrs, g0=(30, 20, 120))
print(r.uncertainty_status, r.k)
```

`r.Rrs`, `r.a`, and `r.bb` cover the input spectrum. `r.u_rel` and `r.u` are available at matched BH4 bands only; other wavelengths are `NaN`.

To correct to another geometry, pass `g1=(solar_zenith, viewing_zenith, relative_azimuth)`. BH4 is then unavailable unless `g1=(0,0,0)`.
