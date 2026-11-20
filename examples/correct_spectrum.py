from pathlib import Path
import numpy as np
import o25

here = Path(__file__).resolve().parent
data = np.loadtxt(here / "data" / "example_spectrum.csv", delimiter=",", skiprows=1)
wl, Rrs = data[:, 0], data[:, 1]
r = o25.correct(wl, Rrs, g0=(30, 20, 120))
print("BH4 class:", r.k)
print("Uncertainty status:", r.uncertainty_status)
np.savetxt(here / "data" / "example_result.csv", np.column_stack((wl, r.Rrs, r.u)),
           delimiter=",", header="wavelength_nm,Rrs_corrected,uncertainty", comments="")
