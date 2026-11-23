# Troubleshooting

## `ModuleNotFoundError: No module named 'o25'`
Activate the intended environment and run `python -m pip install o25`. In a cloned repository, use `python -m pip install -e .`.

## Missing O25 bands
O25 requires bands within ±5 nm of 443, 490, 560 and 665 nm. Check wavelength units and values.

## `missing_bh4_bands`
The O25 correction is valid, but all first 12 OLCI bands were not available, so uncertainty is not provided.

## `unsupported_target_geometry`
O25 corrected to the requested target, but BH4 currently requires target `(0,0,0)`.

## `NaN` uncertainty
`NaN` means BH4 uncertainty is not available at that wavelength. It is not zero uncertainty.

## Geometry order
Always use `(solar zenith, viewing zenith, relative azimuth)` in degrees.
