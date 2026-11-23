"""Load O25 angular coefficients from installed package resources."""
from importlib.resources import as_file, files
import numpy as np
_cached_G_O25_4D=None

def _load(name):
    resource=files("o25").joinpath('data','o25',name)
    try:
        with as_file(resource) as path: return np.loadtxt(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f'Packaged O25 table is missing: {name}') from exc

def get_G_O25_4D():
    global _cached_G_O25_4D
    if _cached_G_O25_4D is None:
        az=np.arange(0,181,15); th=np.r_[np.arange(0,81,10),87.5]
        tables=[_load(n) for n in ('G0w.txt','G1w.txt','G0p.txt','G1p.txt')]
        out=np.full((len(th),len(th),len(az),4),np.nan)
        for i in range(len(az)):
            for j,table in enumerate(tables): out[:,:,i,j]=table[10*i:10*i+10,:]
        _cached_G_O25_4D=out
    return _cached_G_O25_4D
