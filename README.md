# O25: Bidirectional modelling of remote-sensing reflectance and IOP retrieval
**Abstract**

The remote-sensing reflectance (R_rs) varies with the illumination and viewing geometry, an effect referred to as anisotropy, bidirectionality, or bidirectional reflectance distribution function (BRDF). In the aquatic environment, bidirectionality arises from the combined effect of the anisotropic downwelling illumination, scattered by water and particles in varying proportions as a function of the scattering angle, modulated by the two-way interaction with the sea surface. For remote sensing applications, it is desirable that the reflectance only depends on the inherent optical properties (IOPs). This process implies transforming R_rs into a “corrected” or “normalized” R_rs,N , referred to the sun at the zenith and the sensor zenith angle at the nadir. A previous study (D’Alimonte et al., 2025) compared published correction methods, showing the superior performance of a method by Lee et al. (2011, henceforth L11). This article presents a new method starting from L11’s analytical framework, named O25 after OLCI, the Ocean Color sensor on Sentinel-3 satellite. O25 has been calibrated with a recently published synthetic dataset tailored to its needs (Pitarch and Brando, 2024). A comparative assessment using the same datasets as in D’Alimonte et al. (2025) concludes that O25 outperforms L11 and hence all pre-existing methods. O25 includes complementary operational features: (1) applicability range, (2) uncertainty estimates, and (3) a demonstrated reversibility of the bidirectional correction. O25’s look-up tables are generic to any in situ and satellite sensors, including hyperspectral ones. For sensors such as Landsat/Sentinel 2, the IOPs retrieval component of O25 can easily be reformulated.

**Code**
| Version | Location | Key Differences |
|---------|----------|-----------------|
| MATLAB  | `/MATLAB` | Original algorithm |
| Python  | `/o25` | Open-source, NumPy/SciPy port |

**Inquiries to**: jaime.pitarch@cnr.it.
