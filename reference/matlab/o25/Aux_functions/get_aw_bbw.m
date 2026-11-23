function data = get_aw_bbw(l)
%
% Gets water absorption data (WOPP, Roettgers et al. (2016)) and pure
% water backscattering data (Zhang et al. (2009)) and interpolates them to
% the input wavelength. Data are referred to water conditions of 20 ºC and 35 PSU.
% Defines data as persistent in case the code is run in a loop, so it only
% access the data file the first time
%
% data = get_aw_bbw(l)
% Input arguments:
%   l      · nlx1 vector: wavelengths (nm)
% Output arguments:
%   data   · nlx2 vector. First column, water absorption (m^{-1}). Second column, water backscattering (m^{-1}). 
%
% Dependencies:
%    ../data/abs_scat_seawater_20d_35PSU_20230922_short.txt
%
% Jaime Pitarch, CNR-GOS, 07-Feb-2025.

persistent cached_aw_bbw

if isempty(cached_aw_bbw)
    aux_folder=fileparts(mfilename('fullpath'));
    folder_pw=[aux_folder,'\..\Data\'];
    kk = load([folder_pw,'\abs_scat_seawater_20d_35PSU_20230922_short.txt']);
    cached_aw_bbw = interp1(kk(1:end-1, 1),kk(1:end-1,2:3),l);
end
data=cached_aw_bbw;
