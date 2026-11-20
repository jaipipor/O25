# O25

O25 retrieves aquatic inherent optical properties and corrects remote-sensing reflectance (`Rrs`) between illumination-viewing geometries. When the input contains the first 12 OLCI bands and the target is `(0, 0, 0)`, BH4 uncertainty is added automatically.

## Install

```powershell
python -m pip install o25
```

## Minimal use

```python
import o25

r = o25.correct(wl, Rrs, g0=(30, 20, 120))
Rrs_corrected = r.Rrs
uncertainty = r.u
```

Angles are `(solar zenith, viewing zenith, relative azimuth)` in degrees.

## Three rules

- O25 requires unique bands within ±5 nm of 443, 490, 560 and 665 nm.
- If `g1` is omitted, the target defaults to `(0, 0, 0)`.
- BH4 is attempted automatically only for `(0, 0, 0)` and when all 12 required OLCI bands are available. No uncertainty is spectrally interpolated; unmatched wavelengths are `NaN`.

Start with [QUICKSTART.md](QUICKSTART.md), the [example script](examples/correct_spectrum.py), or the [notebook](examples/O25_quickstart.ipynb). Scientific details are in [the user guide](docs/USER_GUIDE.md) and [validation guide](docs/VALIDATION.md).

## Reference

Pitarch et al., *Analytical modeling and correction of the ocean colour bidirectional reflectance across water types*, Remote Sensing of Environment, https://doi.org/10.1016/j.rse.2025.114920

## License

GPL-3.0. Contact: jaime.pitarch@cnr.it
