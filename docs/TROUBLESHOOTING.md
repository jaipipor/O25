# Troubleshooting

This guide lists common messages and direct remedies. Start by reading `r.uncertainty_status` and `r.uncertainty_message`.

## `ModuleNotFoundError: No module named 'o25'`

### In a numbered repository notebook

Keep the notebook inside the downloaded O25 repository and run its first cell before the other cells. The numbered notebooks locate the local package automatically.

The repository should contain both:

```text
examples/01_quickstart.ipynb
o25/__init__.py
```

### In your own Python program

Install O25 in the Python environment used by the program:

```powershell
python -m pip install o25
```

In a cloned repository used for development:

```powershell
python -m pip install -e .
```

## O25 reports missing required bands

O25 requires unique bands within ±5 nm of:

```text
443, 490, 560 and 665 nm
```

Check that:

- wavelengths are expressed in nanometres;
- `wl` contains all four spectral regions;
- wavelength and `Rrs` arrays have the same length;
- there are no duplicated wavelength values.

## `missing_bh4_bands`

The O25 correction is valid, but BH4 uncertainty was not calculated because all first 12 OLCI bands were not available within ±5 nm.

The corrected spectrum remains available through:

```python
r.Rrs
```

## `unsupported_target_geometry`

O25 corrected the spectrum to the requested target, but BH4 uncertainty is currently valid only for target geometry:

```text
(0, 0, 0)
```

This is a BH4 limitation, not an O25 failure.

## `bh4_input_outside_domain`

O25 completed, but the source geometry or spectrum was not valid for the BH4 uncertainty model. Inspect:

```python
print(r.uncertainty_message)
```

## `NaN` values in `r.u` or `r.u_rel`

For hyperspectral input, BH4 uncertainty is returned only at the 12 matched OLCI bands. `NaN` at other wavelengths means uncertainty is not provided there. It does not mean zero uncertainty.

Use:

```python
r.uncertainty_mask
```

to identify wavelengths with native BH4 uncertainty.

## BH4 uncertainty is unavailable for zero or negative Rrs

BH4 feature calculation requires strictly positive, finite `Rrs` at its required bands. O25 may still return a correction, but BH4 uncertainty will not be available.

Check atmospheric-correction outputs, flags and missing-value conventions before replacing or discarding values.

## Geometry appears to produce an unexpected result

Geometry order is always:

```text
(solar zenith, viewing zenith, relative azimuth)
```

All angles are in degrees. Do not interchange solar and viewing zenith.

Example:

```python
g0 = (30, 20, 120)
```

means solar zenith 30°, viewing zenith 20°, relative azimuth 120°.

## Wavelength and Rrs lengths differ

Both arrays must describe the same spectral samples:

```python
len(wl) == len(Rrs)
```

For one correction, both must be one-dimensional.

## The notebook cannot find a CSV file

Keep the notebook and the `examples/data/` directory inside the same downloaded O25 repository. Do not move a notebook alone to another folder.

The numbered notebooks construct data paths from the detected repository root.

## The notebook runs cells out of order

Use:

```text
Kernel → Restart Kernel and Run All Cells
```

This clears old variables and executes the notebook in the intended order.

## The plots do not appear

Install Matplotlib in the Python environment used by Jupyter:

```powershell
python -m pip install matplotlib
```

The notebook examples use ordinary Matplotlib figures and do not require an interactive plotting backend.

## `O25_hyp` still appears in an old script

The historical call remains supported:

```python
from o25 import O25_hyp
```

New code should use:

```python
r = o25.correct(wl, Rrs, g0, g1)
```

because the result object includes uncertainty and status information.

## Asking for help

When reporting a problem, include:

- the full error message;
- Python version;
- O25 version from `o25.__version__`;
- wavelength values;
- source and target geometry;
- `r.uncertainty_status` and `r.uncertainty_message`, if a result was returned.
