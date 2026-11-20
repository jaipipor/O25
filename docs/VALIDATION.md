# Validation and provenance

The test suite separates numerical regression, BH4 exact-node lookup, continuous-geometry interpolation, public API behavior and installed-package resource loading.

The frozen BH4 model contains 744 geometries, four classes, 12 wavelengths and nine stored probabilities. Tests cover every exact class-geometry combination, representative interpolated geometries, geometry boundaries, monotone non-negative quantiles, double-precision runtime arrays and immutable model data.

The retained MATLAB files under `reference/matlab/` are provenance and comparison material, not an alternative user frontend. The legacy Python regression fixture is a change detector and must not be described as independent MATLAB equivalence.
