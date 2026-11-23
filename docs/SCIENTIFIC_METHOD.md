# Scientific method

This document explains what O25 and BH4 do scientifically. It deliberately avoids software architecture and installation details.

## 1. What O25 corrects

Above-water remote-sensing reflectance, `Rrs`, depends not only on the optical properties of the water but also on the illumination and viewing geometry. The same water body can therefore produce different directional `Rrs` spectra under different geometries.

O25 takes:

- a directional above-water `Rrs` spectrum;
- its source geometry `g0`; and
- an optional target geometry `g1`.

O25 then returns the `Rrs` spectrum corresponding to the target geometry.

Geometry is represented as:

```text
(solar zenith, viewing zenith, relative azimuth)
```

All angles are in degrees.

If the target is omitted, O25 uses:

```text
(0, 0, 0)
```

## 2. Spectral information required by O25

O25 requires unique measured bands within ±5 nm of:

```text
443, 490, 560 and 665 nm
```

These bands support retrieval of the inherent optical properties used by the correction. The wavelength matching is one-to-one: one measured wavelength cannot satisfy two nominal bands.

When additional wavelengths are supplied, including a hyperspectral spectrum, O25 returns corrected `Rrs`, absorption and backscattering over the complete input wavelength grid.

## 3. Retrieved inherent optical properties

O25 retrieves:

- total absorption coefficient, `a`, in m⁻¹;
- total backscattering coefficient, `bb`, in m⁻¹.

The class-based implementation separates the scientific operations into:

1. interpolation of pure-water optical properties;
2. retrieval of `a` and `bb` from the directional spectrum;
3. evaluation of angular coefficients at source and target geometries;
4. calculation of corrected `Rrs`.

These internal stages are hidden from ordinary users, who call only:

```python
r = o25.correct(wl, Rrs, g0, g1)
```

## 4. O25 correction between geometries

O25 evaluates the angular model at both the source geometry and the requested target geometry. The retrieved IOPs are then used to calculate target-geometry `Rrs`.

O25 is not restricted to normalization at `(0,0,0)`. The target may be any geometry supported by the O25 angular model.

An identity correction, where `g0 == g1`, returns the input `Rrs` within double-precision numerical tolerance.

## 5. What BH4 adds

BH4 is an empirical uncertainty model for O25 correction to target geometry `(0,0,0)`.

BH4 requires the first 12 OLCI wavelengths, each matched within ±5 nm:

```text
400, 412, 443, 490, 510, 560,
620, 665, 673, 681, 709 and 753 nm
```

BH4 calculates three spectral features from the original directional `Rrs`:

- corrected average visible wavelength;
- visible spectral area;
- a normalized difference index derived from 560 and 665 nm.

The frozen classifier assigns one of four optical classes. The uncertainty model then returns class- and geometry-conditioned empirical quantiles.

## 6. Directional input versus corrected output

The sequence is scientifically important:

1. BH4 classifies the **original directional input spectrum**.
2. O25 corrects the spectrum to the requested target geometry.
3. When the target is `(0,0,0)`, BH4 supplies relative uncertainty for the source geometry and assigned class.
4. O25 converts the relative uncertainty into `Rrs` units using corrected `Rrs`.

The dimensional uncertainty is:

```python
u = u_rel * abs(Rrs_corrected)
```

Therefore:

- `u_rel` is dimensionless;
- `u` has the same units as `Rrs`;
- `u` can be displayed as vertical error bars on corrected `Rrs`.

## 7. Interpretation of BH4 uncertainty

The default probability is:

```text
p = 0.68
```

Other stored probabilities can be selected through the `p` argument. These values are empirical quantiles conditioned on BH4 class and geometry. They should not automatically be described as standard deviations or conventional confidence intervals.

## 8. Hyperspectral limitation

O25 can correct a full hyperspectral input. BH4, in its current form, is calibrated only at the first 12 OLCI wavelengths.

Consequently:

- corrected `Rrs`, `a` and `bb` cover the complete input grid;
- `u_rel` and `u` are finite only at the 12 matched BH4 bands;
- other uncertainty values are `NaN`;
- `NaN` means uncertainty is not provided, not zero;
- version 0.2 does not interpolate uncertainty between wavelengths.

The `uncertainty_mask` output identifies the positions with native BH4 uncertainty.

## 9. Numerical precision

Runtime calculations are carried out in double precision. The frozen BH4 quantile table retains its documented storage precision and is converted to double precision when loaded.

## 10. Applicability is reported, not hidden

If BH4 cannot be applied, O25 still returns a valid correction whenever the four O25 bands are available. The result explains the limitation through:

```python
r.uncertainty_status
r.uncertainty_message
```

This distinction prevents failure of the O25 correction merely because uncertainty is unavailable.
