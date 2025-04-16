import numpy as np
from scipy.interpolate import RegularGridInterpolator
from Aux_functions.get_aw_bbw import get_aw_bbw
from Aux_functions.get_G_O25_4D import get_G_O25_4D

def O25_hyp(l, Rrs, geom_old, geom_new):
    """
    O25: semianalytical IOP retrieval and bidirectional correction method of Rrs
    Works with individual spectra.

    Parameters:
    -----------
    l : array_like
        nl x 1 vector of wavelengths (nm)
    Rrs : array_like
        nl x 1 vector of Remote-sensing reflectance (sr^-1)
    geom_old : array_like
        3 x 1 vector of original geometry [sun_zenith, view_zenith, rel_azimuth] (degrees)
    geom_new : array_like
        3 x 1 vector of new geometry [sun_zenith, view_zenith, rel_azimuth] (degrees)

    Returns:
    --------
    a : ndarray
        nl x 1 vector of total absorption coefficient (m^-1)
    bb : ndarray
        nl x 1 vector of total backscattering coefficient (m^-1)
    Rrs_N : ndarray
        nl x 1 vector of Rrs corrected to geom_new geometry
    """
    # Get water properties
    data = get_aw_bbw(l)
    aw = data[:, 0]
    bbw = data[:, 1]
    
    # Ensure column vectors
    l = np.asarray(l).flatten()
    Rrs = np.asarray(Rrs).flatten()
    
    # Find bands and average Rrs
    i_2 = np.where((l > 440) & (l < 446) & ~np.isnan(Rrs))[0]
    R2 = np.nanmean(Rrs[i_2])
    
    i_3 = np.where((l > 487) & (l < 493) & ~np.isnan(Rrs))[0]
    R3 = np.nanmean(Rrs[i_3])
    
    i_5 = np.where((l > 554) & (l < 566) & ~np.isnan(Rrs))[0]
    R5 = np.nanmean(Rrs[i_5])
    
    i_6 = np.where((l > 662) & (l < 668) & ~np.isnan(Rrs))[0]
    R6 = np.nanmean(Rrs[i_6])
    
    # Get G 4D data and setup grids
    G_4D = get_G_O25_4D()
    az_l = np.arange(0, 181, 15)  # 0:15:180
    th_v_l = np.concatenate([np.arange(0, 81, 10), [87.5]])  # [0:10:80 87.5]
    th_s_l = np.concatenate([np.arange(0, 81, 10), [87.5]])  # [0:10:80 87.5]
    
    # Create interpolators for each G component
    def create_interpolator(channel):
        return RegularGridInterpolator((th_s_l, th_v_l, az_l), 
                                      G_4D[:, :, :, channel], 
                                      bounds_error=False, fill_value=None)
    
    # Interpolate for original geometry
    G0w = create_interpolator(0)(geom_old)
    G1w = create_interpolator(1)(geom_old)
    G0p = create_interpolator(2)(geom_old)
    G1p = create_interpolator(3)(geom_old)
    
    # Interpolate for new geometry
    G0w_N = create_interpolator(0)(geom_new)
    G1w_N = create_interpolator(1)(geom_new)
    G0p_N = create_interpolator(2)(geom_new)
    G1p_N = create_interpolator(3)(geom_new)
    
    # Calculate eta and chi
    eta = 1.433 * (1 - 0.5091 * np.exp(-0.8671 * np.log10(R2 / R5)))  # PB24
    
    # RGB parameters
    p_chi = -np.array([0.140559039379002, 0.102529719530837, 
                       1.141618978662982, 1.258673459838637])  # PB24
    chi = np.log10((R2 + R3) / (R5 + 5 * R6**2 / R3))
    
    # Calculate bbp0
    aw0 = np.nanmean(aw[i_5])
    bbw0 = np.nanmean(bbw[i_5])
    al0 = aw0 + 10**np.polyval(p_chi, chi)
    
    C0 = G0w * bbw0 * (al0 + bbw0) - R5 * (al0 + bbw0)**2 + G1w * bbw0**2
    C1 = G0w * bbw0 + G0p * (al0 + bbw0) - 2 * R5 * (al0 + bbw0)
    C2 = G0p + G1p - R5
    
    bbp0 = (np.sqrt(C1**2 - 4 * C2 * C0) - C1) / (2 * C2)
    bbp = bbp0 * (l[i_5[0]] / l)**eta  # Using first index of i_5 as representative
    bb = bbp + bbw
    
    # Calculate absorption
    D0 = G1w * bbw**2 + G1p * bbp**2
    D1 = G0w * bbw + G0p * bbp
    
    a = -(bbw + bbp) + (np.sqrt(D1**2 + 4 * Rrs * D0) + D1) / (2 * Rrs)
    k = a + bb
    
    # Calculate normalized Rrs
    Rrs_N = (G0w_N + G1w_N * bbw / k) * bbw / k + (G0p_N + G1p_N * bbp / k) * bbp / k
    
    return a, bb, Rrs_N