import numpy as np
import os
from pathlib import Path

# Module-level cache (Python's equivalent to MATLAB's persistent)
_cached_G_O25_4D = None

def get_G_O25_4D():
    """
    Gets O25's "G" coefficients for angular modelling of Rrs
    Uses module-level caching to only load data once

    Returns:
    --------
    data : ndarray
        13x13x10x4 hyper-matrix where:
        - First dimension: sun zenith angle (degrees)
        - Second dimension: view zenith angle (degrees) 
        - Third dimension: relative azimuth angle (degrees)
        - Fourth dimension: G parameters (0w, 1w, 0p, 1p)
    """
    global _cached_G_O25_4D
    
    if _cached_G_O25_4D is None:
        # Define angle grids (matches MATLAB code)
        az_l = np.arange(0, 181, 15)       # 0:15:180
        th_v_l = np.concatenate([np.arange(0, 81, 10), [87.5]])  # [0:10:80 87.5]
        th_s_l = np.concatenate([np.arange(0, 81, 10), [87.5]])  # [0:10:80 87.5]
        
        # Get path to data files
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        data_folder = current_dir.parent / '../data'
        
        
        # Load each coefficient matrix
        try:
            Gw0_m = np.loadtxt(data_folder / 'G0w.txt')
            Gw1_m = np.loadtxt(data_folder / 'G1w.txt')
            Gp0_m = np.loadtxt(data_folder / 'G0p.txt')
            Gp1_m = np.loadtxt(data_folder / 'G1p.txt')
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not find G coefficient files in {data_folder}") from e
        
        # Initialize 4D array (13x13x10x4)
        N_th_s = len(th_s_l)
        N_th_v = len(th_v_l)
        N_az = len(az_l)
        _cached_G_O25_4D = np.full((N_th_s, N_th_v, N_az, 4), np.nan)
        
        # Populate the 4D array (MATLAB uses 1-based indexing)
        for i in range(N_az):
            start_row = 10 * i
            end_row = start_row + 10
            
            _cached_G_O25_4D[:, :, i, 0] = Gw0_m[start_row:end_row, :]  # G0w
            _cached_G_O25_4D[:, :, i, 1] = Gw1_m[start_row:end_row, :]  # G1w
            _cached_G_O25_4D[:, :, i, 2] = Gp0_m[start_row:end_row, :]  # G0p
            _cached_G_O25_4D[:, :, i, 3] = Gp1_m[start_row:end_row, :]  # G1p
    
    return _cached_G_O25_4D