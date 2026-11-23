# User guide

## Inputs

`o25.correct(wl, Rrs, g0, g1=None, p=0.68)` accepts one one-dimensional spectrum. Wavelengths are in nm, `Rrs` in sr⁻¹, and geometries are three angles in degrees: solar zenith, viewing zenith, relative azimuth.

O25 uses bands within ±5 nm of 443, 490, 560 and 665 nm. Matching is one-to-one, so one measured wavelength cannot satisfy two nominal bands.

## Outputs

- `Rrs`: corrected remote-sensing reflectance
- `a`: total absorption coefficient in m⁻¹
- `bb`: total backscattering coefficient in m⁻¹
- `u_rel`: selected BH4 relative uncertainty
- `u`: dimensional uncertainty, `u_rel * abs(Rrs)`
- `k`: BH4 optical class, 1–4
- `uncertainty_status` and `uncertainty_message`: applicability explanation

## BH4 behavior

BH4 requires all first 12 OLCI bands near 400, 412, 443, 490, 510, 560, 620, 665, 673, 681, 709 and 753 nm, under the same ±5 nm tolerance. It is available only for target geometry `(0,0,0)`. For hyperspectral input, uncertainty is returned only at the 12 matched bands; other values are `NaN`.

All runtime calculations are performed in double precision. The frozen BH4 table retains its documented storage precision and is converted to double on loading.

## Repeated processing

`model = o25.O25Model()` exposes the same `.correct(...)` call. The model stores no previous spectrum, output path, plotting state or mutable options.
