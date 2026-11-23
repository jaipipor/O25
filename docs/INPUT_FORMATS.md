# Input formats

O25 expects a one-dimensional wavelength array in nanometres and a one-dimensional above-water `Rrs` array in sr⁻¹ with the same length. Geometry is `(solar zenith, viewing zenith, relative azimuth)` in degrees.

O25 requires unique bands within ±5 nm of 443, 490, 560 and 665 nm. BH4 requires the first 12 OLCI bands within the same tolerance and strictly positive finite `Rrs` at those bands.

The example CSV files use a header row and ordinary decimal numbers. Missing BH4 uncertainty is saved as `nan`; `nan` means not provided, not zero.
