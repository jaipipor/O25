function data = get_G_O25_4D
%
% Gets O25's "G" coefficients for angular modelling of Rrs
% Defines data as persistent in case the code is run in a loop, so it only
% access the data file the first time
%
% data = get_G_O25_4D
% Input arguments:
%   none
% Output arguments:
%   data   · 13x13x10x4 hyper-matrix.
%               First dimension runs along the sun zenith angle (º) 
%               Second dimension runs along the view zenith angle (º) 
%               Third dimension runs along the relative azimuth angle (º) 
%               Fourth dimension stands for every "G" parameter
%
% Dependencies:
%    ../data/G0w.txt
%    ../data/G0p.txt
%    ../data/G1w.txt
%    ../data/G1p.txt
%
% Jaime Pitarch, CNR-GOS, 07-Feb-2025.

persistent cached_G_O25_4D

if isempty(cached_G_O25_4D)  
    az_l=0:15:180;N_az_l=length(az_l);
    th_v_l=[0:10:80 87.5];N_th_v_l=length(th_v_l);
    th_s_l=[0:10:80 87.5];N_th_s_l=length(th_s_l);
    
    %-----------------------------------
    %Dimensions: th_v_l, az_l, th_s_l
    aux_folder=fileparts(mfilename('fullpath'));
    folder_G=[aux_folder,'\..\Data\'];
    Gw0_m=load([folder_G,'G0w.txt']);
    Gp0_m=load([folder_G,'G0p.txt']);
    Gw1_m=load([folder_G,'G1w.txt']);
    Gp1_m=load([folder_G,'G1p.txt']);
    
    cached_G_O25_4D=nan(N_th_s_l,N_th_v_l,N_az_l,4);
    
    for i=1:N_az_l
        cached_G_O25_4D(:,:,i,1)=Gw0_m((1:10)+10*(i-1),:);
        cached_G_O25_4D(:,:,i,2)=Gw1_m((1:10)+10*(i-1),:);
        cached_G_O25_4D(:,:,i,3)=Gp0_m((1:10)+10*(i-1),:);
        cached_G_O25_4D(:,:,i,4)=Gp1_m((1:10)+10*(i-1),:);
    end
end
data=cached_G_O25_4D;