## 📆 O25: Retrieval of IOPs and Bidirectional Correction for In Situ and Satellite Data

The remote-sensing reflectance (R_rs) varies with the illumination and viewing geometry, an effect referred to as anisotropy, bidirectionality, or bidirectional reflectance distribution function (BRDF). In the aquatic environment, bidirectionality arises from the combined effect of the anisotropic downwelling illumination, scattered by water and particles in varying proportions as a function of the scattering angle, modulated by the two-way interaction with the sea surface. For remote sensing applications, it is desirable that the reflectance only depends on the inherent optical properties (IOPs). This process implies transforming R_rs into a “corrected” or “normalized” R_rs,N , referred to the sun at the zenith and the sensor zenith angle at the nadir. A previous study (D’Alimonte et al., 2025) compared published correction methods, showing the superior performance of a method by Lee et al. (2011, henceforth L11). This article presents a new method starting from L11’s analytical framework, named **O25** after OLCI, the Ocean Color sensor on Sentinel-3 satellite. O25 has been calibrated with a recently published synthetic dataset tailored to its needs (Pitarch and Brando, 2024). A comparative assessment using the same datasets as in D’Alimonte et al. (2025) concludes that O25 outperforms L11 and hence all pre-existing methods. O25 includes complementary operational features: (1) applicability range, (2) uncertainty estimates, and (3) a demonstrated reversibility of the bidirectional correction. O25’s look-up tables are generic to any in situ and satellite sensors, including hyperspectral ones. For sensors such as Landsat/Sentinel 2, the IOPs retrieval component of O25 can easily be reformulated.

---

## 🚀 Main Features

- **IOP Retrieval**: Estimates absorption and backscattering coefficients from Rrs.
- **Bidirectional Correction**: Adjusts Rrs for different observation geometries.
- **Uncertainty Estimation**: Provides uncertainty estimates for the retrieved IOPs.
- **Reversibility**: Allows reverse bidirectional correction for validation purposes.
- **Compatibility**: Works with any in situ or satellite sensor, including Landsat and Sentinel-2.

---

## 🛠️ Installation

Install the latest version of O25 from PyPI:

```bash
pip install o25
```

---

## 📚 Basic Usage

```python
from o25 import O25_hyp

# Define inputs
l = [...]  # Wavelengths in nm
Rrs = [...]  # Remote sensing reflectance
geom_old = [...]  # Original geometry: [solar zenith angle, viewing zenith angle, relative azimuth angle]
geom_new = [...]  # New geometry

# Run O25
a, bb, Rrs_N = O25_hyp(l, Rrs, geom_old, geom_new)
```

---

## 📄 Reference paper

Jaime Pitarch, Vittorio Ernesto Brando, Marco Talone, Constant Mazeran, Davide D'Alimonte, Tamito Kajiyama, Ewa Kwiatkowska, David Dessailly, Juan Ignacio Gossn,
*Analytical modeling and correction of the ocean colour bidirectional reflectance across water types*, Remote Sensing of Environment, https://doi.org/10.1016/j.rse.2025.114920.

---

## 📊 Documentation

For a detailed description of the functions and parameters, see the [full documentation](https://github.com/jaipipor/O25/wiki).
(Now empty, please refer to the commented function O25_hyp.py)

---

## 🧪 Examples

You can find usage examples in the [`examples/`](https://github.com/jaipipor/O25/tree/main/examples) directory.
(Now empty, please refer to the commented function O25_hyp.py)

---

## 📝 License

This project is licensed under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request to suggest improvements or report bugs.

---

**Code versions**
| Version | Location | Key Differences |
|---------|----------|-----------------|
| MATLAB  | `/MATLAB` | Original algorithm |
| Python  | `/o25` | Open-source, NumPy/SciPy port |

---

## 📢 Contact

Inquiries to jaime.pitarch@cnr.it.
