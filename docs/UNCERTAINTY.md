# BH4 uncertainty

BH4 is applied automatically when the target geometry is `(0,0,0)` and all first 12 OLCI bands are available within ±5 nm. It returns a class identifier `k`, relative uncertainty `u_rel`, and dimensional uncertainty `u = u_rel × |Rrs corrected|`.

The default stored probability is `p=0.68`. The values are empirical class- and geometry-conditioned bounds, not automatically standard deviations.

O25 may correct a complete hyperspectral spectrum, but BH4 uncertainty is returned only at the matched OLCI bands. Non-OLCI wavelengths contain `NaN` in `u` and `u_rel`; version 0.2 performs no spectral uncertainty interpolation.
