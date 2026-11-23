# O25

O25 corrects above-water remote-sensing reflectance (`Rrs`) from one illumination-viewing geometry to another and retrieves total absorption (`a`) and total backscattering (`bb`). When the observation satisfies the BH4 requirements, O25 also returns an empirical uncertainty estimate automatically.

## New to O25?

Start with **[Notebook 01: Quick start](examples/01_quickstart.ipynb)**. It performs one complete correction, explains every input and output, and plots corrected `Rrs` with uncertainty bars in `Rrs` units.

The notebooks are ordered from introductory to more advanced:

1. [One spectrum: quick start](examples/01_quickstart.ipynb)
2. [Files and hyperspectral data](examples/02_files_and_hyperspectral_data.ipynb)
3. [Multiple spectra](examples/03_multiple_spectra.ipynb)

A compact non-interactive example is also available in [`examples/correct_spectrum.py`](examples/correct_spectrum.py).

## Installation

O25 requires Python 3.10 or newer.

```powershell
python -m pip install o25
```

For the example notebooks and plots:

```powershell
python -m pip install matplotlib jupyterlab
```

Users working from a downloaded copy of this repository can open the numbered notebooks directly. The notebooks locate the local O25 package automatically.

## Minimal use

```python
import o25

r = o25.correct(
    wl,
    Rrs,
    g0=(30, 20, 120),
)

Rrs_corrected = r.Rrs
uncertainty = r.u
```

Geometry is always written as:

```text
(solar zenith, viewing zenith, relative azimuth)
```

Angles are in degrees. If `g1` is omitted, the target geometry is `(0, 0, 0)`.

## Main outputs

| Output | Meaning | Units |
|---|---|---|
| `r.Rrs` | O25-corrected remote-sensing reflectance | sr⁻¹ |
| `r.a` | Total absorption coefficient | m⁻¹ |
| `r.bb` | Total backscattering coefficient | m⁻¹ |
| `r.k` | BH4 optical class, from 1 to 4 | dimensionless |
| `r.u_rel` | Relative BH4 uncertainty | dimensionless |
| `r.u` | Dimensional BH4 uncertainty | same units as `Rrs` |
| `r.uncertainty_status` | Short machine-readable status | text |
| `r.uncertainty_message` | Human-readable explanation | text |

Dimensional uncertainty is calculated as:

```python
r.u = r.u_rel * abs(r.Rrs)
```

The notebooks display `r.u` as vertical error bars on corrected `Rrs`.

## Applicability rules

### O25 correction

O25 requires one unique measured band within ±5 nm of each nominal wavelength:

```text
443, 490, 560 and 665 nm
```

O25 can correct from one valid geometry to any other valid geometry.

### BH4 uncertainty

BH4 is attempted automatically only when:

- the target geometry is `(0, 0, 0)`; and
- all first 12 OLCI wavelengths are available within ±5 nm:

```text
400, 412, 443, 490, 510, 560,
620, 665, 673, 681, 709 and 753 nm
```

If BH4 cannot be applied, a valid O25 correction is still returned. Inspect:

```python
r.uncertainty_status
r.uncertainty_message
```

For hyperspectral input, O25 corrects the complete spectrum. BH4 uncertainty is returned only at the 12 matched OLCI bands. Other uncertainty values are `NaN`. Version 0.2 does not interpolate uncertainty spectrally.

## Correcting to another geometry

```python
r = o25.correct(
    wl,
    Rrs,
    g0=(30, 20, 120),
    g1=(40, 10, 75),
)
```

The O25 correction is returned, but BH4 uncertainty is unavailable unless `g1=(0,0,0)`.

## Repeated processing

Most users only need `o25.correct(...)`. For repeated calculations, the same loaded model can be reused:

```python
model = o25.O25Model()

results = [
    model.correct(wl, spectrum, geometry)
    for spectrum, geometry in zip(spectra, geometries)
]
```

The model does not retain the previous spectrum or result.

## Documentation

- [Scientific method](docs/SCIENTIFIC_METHOD.md)
- [Uncertainty](docs/UNCERTAINTY.md)
- [Input formats](docs/INPUT_FORMATS.md)
- [Examples](docs/EXAMPLES.md)
- [Validation](docs/VALIDATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Compatibility

O25 0.2 uses a class-based numerical core and the `o25.correct(...)` frontend. Scripts using the historical `O25_hyp(...)` function remain supported through a compatibility wrapper:

```python
from o25 import O25_hyp

a, bb, Rrs_corrected = O25_hyp(wl, Rrs, g0, g1)
```

New code should use `o25.correct(...)`.

## Reference

Pitarch et al., *Analytical modeling and correction of the ocean colour bidirectional reflectance across water types*, Remote Sensing of Environment. https://doi.org/10.1016/j.rse.2025.114920

## License

O25 is distributed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE).
