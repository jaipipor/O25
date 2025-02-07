function [a,bb,Rrs_N]=O25_hyp(l,Rrs,geom_old,geom_new)
%
% O25: semianalytical IOP retrieval and bidirectional correction method of Rrs
% Works with individual spectra.
%
% [a,bb,Rrs_N]=O25_hyp(l,Rrs,geom_old,geom_new)
% Input arguments:
%   l       · nlx1 vector: wavelengths (nm)
%   Rrs     · nlx1 vector: Remote-sensing reflectance associated to the above wavelengths (sr)
%   geom_old· 3x1  vector: a triplet representing (1) the sun zenith angle (º), the view zenith angle (º) and the relative azimuth (º) of the original Rrs observation
%   geom_new· 3x1  vector: a triplet representing (1) the sun zenith angle
%   (º), the view zenith angle (º) and the relative azimuth (º) of the corrected Rrs
% Output arguments:
%   a        · nlx1 vector: total absorption coefficient (m^{-1})
%   bb       · nlx1 vector: total backscattering coefficient (m^{-1})
%   Rrs_N    · nlx1 vector: Rrs referred at geom_new
%
% Dependencies:
%    ./Aux_functions/get_aw_bbw.m
%    ./Aux_functions/get_G_4D.m
%
% Jaime Pitarch, CNR-GOS, 07-Feb-2025.

% Example run:
% my_Ed =[0.00089262    0.0069923     0.018696    0.0023898
%        1.65e-06   9.9975e-05   0.00075004   5.8526e-06
%        0.058626      0.14587      0.14568     0.035567];
%    PAR = PAR_from_Ed_380_443_490_560(my_Ed);

data = get_aw_bbw(l);
aw=data(:,1);
bbw=data(:,2);

l=l(:);%column
Rrs=Rrs(:);%column

i_2=find(l>440&l<446&~isnan(Rrs));R2=nanmean(Rrs(i_2));
i_3=find(l>487&l<493&~isnan(Rrs));R3=nanmean(Rrs(i_3));
i_5=find(l>554&l<566&~isnan(Rrs));R5=nanmean(Rrs(i_5));
i_6=find(l>662&l<668&~isnan(Rrs));R6=nanmean(Rrs(i_6));

G_4D = get_G_O25_4D;
az_l=0:15:180;
th_v_l=[0:10:80 87.5];
th_s_l=[0:10:80 87.5];

G0w=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,1),geom_old(1),geom_old(2),geom_old(3));
G1w=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,2),geom_old(1),geom_old(2),geom_old(3));
G0p=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,3),geom_old(1),geom_old(2),geom_old(3));
G1p=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,4),geom_old(1),geom_old(2),geom_old(3));

G0w_N=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,1),geom_new(1),geom_new(2),geom_new(3));
G1w_N=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,2),geom_new(1),geom_new(2),geom_new(3));
G0p_N=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,3),geom_new(1),geom_new(2),geom_new(3));
G1p_N=interpn(th_s_l,th_v_l,az_l,G_4D(:,:,:,4),geom_new(1),geom_new(2),geom_new(3));

eta=1.433*(1-0.5091*exp(-0.8671*log10(R2/R5)));%PB24
%-------RGB----------------
p_chi=-[0.140559039379002  0.102529719530837  1.141618978662982  1.258673459838637];%%PB24
chi=log10((R2+R3)/(R5+5*R6^2/R3));
%-------End of RGB----------------

aw0=nanmean(aw(i_5));bbw0=nanmean(bbw(i_5));
al0=aw0+10^polyval(p_chi,chi);

C0=G0w*bbw0*(al0+bbw0)-R5*(al0+bbw0)^2+G1w*bbw0^2;
C1=G0w*bbw0+G0p*(al0+bbw0)-2*R5*(al0+bbw0);
C2=G0p+G1p-R5;

bbp0=(sqrt(C1^2-4*C2*C0)-C1)/(2*C2);
bbp=bbp0*(l(i_5)./l).^eta;
bb=bbp+bbw;

D0=G1w*bbw.^2+G1p*bbp.^2;
D1=G0w*bbw+G0p*bbp;

a=-(bbw+bbp)+(sqrt(D1.^2+4*Rrs.*D0)+D1)./(2*Rrs);
k=a+bb;

Rrs_N=(G0w_N+G1w_N*bbw./k).*bbw./k+(G0p_N+G1p_N*bbp./k).*bbp./k;