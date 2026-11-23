# Validation

This document states what the O25 0.2 test suite establishes and what it does not establish.

## 1. O25 core migration

O25 0.2 replaces the operational monolithic procedural core with a class-based `O25Model` and separate numerical components for:

- angular coefficients;
- pure-water optical properties and IOP retrieval;
- bidirectional `Rrs` correction.

The previous procedural Python implementation is retained only under `tests/reference/`. It is not installed with O25 and is not used during normal execution.

## 2. Procedural versus class-based equivalence

The migration-equivalence suite compares the old procedural implementation directly with the new class-based implementation.

The comparison includes 62 independent numerical cases:

- 36 structured cases from three spectral grids, four positive spectral shapes and three geometry transformations;
- six edge cases, including identity corrections, angular boundaries, zero solar zenith and zero viewing zenith;
- 20 deterministic seeded hyperspectral cases with arbitrary in-domain source and target geometries.

The tested spectral grids are:

- the minimum four O25 bands;
- the first 12 OLCI bands;
- a 1 nm hyperspectral grid from 350 to 800 nm.

For every case, the suite compares:

```text
a
bb
corrected Rrs
```

The numerical thresholds are:

```text
relative tolerance: 2 × 10⁻¹⁴
absolute tolerance: 2 × 10⁻¹⁵
```

All migration-equivalence cases pass.

These tests establish equivalence over the tested spectra and geometry domain. They do not claim universal equivalence for every mathematically possible input.

## 3. Public-interface consistency

The test suite verifies that the following interfaces use the same class-based numerical core and return identical O25 values:

```python
o25.correct(...)
o25.O25Model().correct(...)
o25.O25_hyp(...)
```

`O25_hyp` is only a compatibility wrapper. The installed numerical core contains no active monolithic `O25_hyp` implementation.

A clean-process architecture test confirms that normal O25 execution does not import the test-only procedural reference.

## 4. BH4 model integrity

The frozen BH4 model loader validates:

- model and source-production versions;
- four-class configuration;
- 744 stored geometries;
- 12 wavelengths;
- nine stored probabilities;
- classifier dimensions;
- quantile dimensions and ordering;
- class-geometry support;
- interpolation metadata;
- runtime precision metadata.

Exposed numerical model arrays are converted to double precision and made read-only.

## 5. Exact-node BH4 lookup

The exact-node suite covers all:

```text
4 classes × 744 geometries = 2,976 combinations
```

For every combination, Python returns the corresponding frozen quantiles and class-geometry support.

The suite also checks:

- probability-by-wavelength orientation;
- class identifiers 1–4;
- canonical relative azimuth handling;
- azimuth-degenerate cases when solar or viewing zenith is zero;
- rejection of non-node geometries by the exact-node interface.

## 6. Continuous BH4 geometry

Continuous geometry uses sequential PCHIP interpolation of non-negative probability increments in the documented order:

```text
canonical relative azimuth → viewing zenith → solar zenith
```

Tests cover:

- exact-node bypass;
- representative off-node geometries;
- geometry boundaries;
- non-negative increments;
- non-decreasing reconstructed quantiles;
- rejection of out-of-domain zenith angles;
- single-spectrum and repeated-spectrum operation.

## 7. Integrated O25-BH4 workflow

The public API tests verify:

- automatic BH4 application at target `(0,0,0)`;
- O25-only operation for other target geometries;
- O25-only operation when BH4 bands are missing;
- class, relative uncertainty and dimensional uncertainty outputs;
- native OLCI placement in hyperspectral arrays;
- explicit `NaN` uncertainty outside the 12 matched bands;
- absence of spectral uncertainty interpolation;
- dimensionalization as `u_rel × |Rrs corrected|`.

## 8. Installation and supported Python versions

GitHub Actions runs the repository tests on Python 3.10, 3.11, 3.12 and 3.13.

Installation tests verify that the packaged distribution includes:

- O25 coefficient tables;
- the pure-water optical table;
- the frozen BH4 MAT model.

The installed package is exercised from outside the repository working directory.

## 9. Notebook and example validation

The three numbered notebooks are intended to be executable from top to bottom. They cover:

- one 12-band correction with dimensional uncertainty bars;
- hyperspectral CSV processing with native-band uncertainty;
- repeated processing with one reusable `O25Model`.

Notebook execution should be included in continuous integration so that broken imports, paths, cells or plots are detected automatically.

## 10. Scope of the claims

The validation establishes:

- numerical equivalence of the new O25 core to the previous operational Python implementation over the documented migration cases;
- integrity and exhaustive exact-node access of the frozen BH4 model;
- tested behavior of continuous BH4 geometry interpolation;
- consistency of the public interfaces;
- correct packaging of runtime scientific resources.

The validation does not establish:

- independent experimental validation of O25 or BH4;
- uncertainty outside the 12 calibrated BH4 wavelengths;
- spectral interpolation of uncertainty;
- BH4 applicability for target geometries other than `(0,0,0)`;
- universal equivalence outside the tested numerical domain.
