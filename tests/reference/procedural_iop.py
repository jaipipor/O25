"""Load pure-water optical properties from installed package resources."""
from importlib.resources import as_file, files
import numpy as np
from scipy.interpolate import interp1d
_cached_interpolator=None

def get_aw_bbw(l):
    global _cached_interpolator
    l=np.asarray(l).flatten()
    if _cached_interpolator is None:
        resource=files("o25").joinpath('data','o25','abs_scat_seawater_20d_35PSU_20230922_short.txt')
        try:
            with as_file(resource) as path: table=np.loadtxt(path,comments='%')
        except FileNotFoundError as exc:
            raise FileNotFoundError('Packaged O25 water-properties table is missing.') from exc
        x=table[:-1,0]
        _cached_interpolator=(
            interp1d(x,table[:-1,1],kind='linear',bounds_error=False,fill_value='extrapolate'),
            interp1d(x,table[:-1,2],kind='linear',bounds_error=False,fill_value='extrapolate'))
    return np.column_stack((_cached_interpolator[0](l),_cached_interpolator[1](l)))
