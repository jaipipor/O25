"""Small non-interactive O25 example using a CSV spectrum."""
from pathlib import Path
import numpy as np
import o25

here = Path(__file__).resolve().parent
data = np.loadtxt(here / "data" / "olci_spectrum.csv", delimiter=",", skiprows=1)
wl, Rrs = data[:, 0], data[:, 1]

r = o25.correct(wl, Rrs, g0=(30, 20, 120))

print("BH4 class:", r.k)
print("Uncertainty probability:", r.p)
print("Uncertainty status:", r.uncertainty_status)

output = np.column_stack((wl, Rrs, r.Rrs, r.u))
np.savetxt(
    here / "data" / "olci_result.csv",
    output,
    delimiter=",",
    header="wavelength_nm,Rrs_input,Rrs_corrected,uncertainty",
    comments="",
)
