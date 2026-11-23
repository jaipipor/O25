# Examples

The examples are a progressive learning sequence. Users new to Python should open `examples/01_quickstart.ipynb` and run cells from top to bottom.

The main scientific visualization for a single spectrum is corrected `Rrs` with vertical error bars given by `r.u`. These bars have the same units as `Rrs` because `u = u_rel × |Rrs corrected|`. The stored probability, normally `p=0.68`, is shown in the legend and must not automatically be called one standard deviation.

For hyperspectral input, uncertainty is plotted only at the 12 matched BH4 bands. No line or shaded envelope is drawn across uncalibrated wavelengths.
