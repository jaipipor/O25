import numpy as np
import os
from pathlib import Path
from scipy.interpolate import interp1d

# Module-level cache (equivalent to MATLAB's persistent)
_cached_data = None
_cached_interpolator = None

def get_aw_bbw(l):
    """
    Gets water absorption (WOPP, Roettgers et al. 2016) and pure water backscattering
    (Zhang et al. 2009) data, interpolated to input wavelengths (20°C, 35 PSU).

    Parameters:
    -----------
    l : array_like
        Wavelengths in nm (nl x 1 vector)

    Returns:
    --------
    data : ndarray
        nl x 2 array where:
        - First column: water absorption (m^-1)
        - Second column: water backscattering (m^-1)
    """
    global _cached_data, _cached_interpolator
    
    l = np.asarray(l).flatten()
    
    # Load and cache data on first call
    if _cached_interpolator is None:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        data_file = current_dir.parent / '../data' / 'abs_scat_seawater_20d_35PSU_20230922_short.txt'
        
        try:
            kk = np.loadtxt(data_file, comments='%')  # Skip lines starting with %
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Water properties data file not found at {data_file}") from e
        
        # Create interpolators for aw and bbw
        wavelengths = kk[:-1, 0]  # Exclude last row if it's footer
        _cached_interpolator = (
            interp1d(wavelengths, kk[:-1, 1], kind='linear', bounds_error=False, fill_value='extrapolate'),  # aw
            interp1d(wavelengths, kk[:-1, 2], kind='linear', bounds_error=False, fill_value='extrapolate')   # bbw
        )
    
    # Interpolate to requested wavelengths
    aw = _cached_interpolator[0](l)
    bbw = _cached_interpolator[1](l)
    
    return np.column_stack((aw, bbw))