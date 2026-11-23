# O25 examples

Start with **01_quickstart.ipynb**. The notebooks are ordered from one simple spectrum to file-based hyperspectral processing and then multiple spectra.

- `01_quickstart.ipynb`: one 12-band spectrum, automatic BH4, and dimensional uncertainty as error bars.
- `02_files_and_hyperspectral_data.ipynb`: CSV input/output, full hyperspectral correction, native-band uncertainty, and arbitrary target geometry.
- `03_multiple_spectra.ipynb`: repeated processing with `O25Model` and batch summaries.
- `correct_spectrum.py`: compact non-interactive reference and smoke test.

For the plots, install Matplotlib in addition to O25:

```powershell
python -m pip install matplotlib jupyterlab
```

Then start JupyterLab from the `examples` directory:

```powershell
cd examples
jupyter lab
```
