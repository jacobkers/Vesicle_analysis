function FanalistaWorldMapper
%This function loads a tiff stack of a spherical object and performs a 3D
%sampling on it to get a surface map. JacobKers 2017.

%Steps:
% % QI track 
% radial profile max ? x0,y0,z0,rxy. 
% Define phi, theta, r grid (include z rxy/rz correction); 
% sample via 3D interpolation (include z-scaling); 
% average over r range. Plot phi, theta map
%------------------------------------------------------------------------

%settings
flipit=1;  %1=flipYZ, %2=flip XZ
manualclick=0;
equator=20    %20  %50;
trackplane=20;
southpole=5  %5 %31;
skindepth=2;  %pixels

close all;
% Get the images
codepth='C:\Users\jkerssemakers\Dropbox\CD_recent\BN_CD16_Fede\2017_MatLabCode_WorldMapper';
%inpth='D:\jkerssemakers\My Documents\BN CD Data\2016_Fede\17-03-16 Droplets FtsZ\_3\';
%insubdir='good2_decon_crop_lipo2\';
inpth='C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_Meshworks\';
insubdir='stack - background\';  %southpole 5
%insubdir='stack\';
cd(strcat(inpth,insubdir));
tiflist=dir('*.tif');
cd(codepth);
[ff,~]=size(tiflist);
equatorim=double(imread(strcat(inpth,insubdir,tiflist(equator).name)));
trackim=double(imread(strcat(inpth,insubdir,tiflist(trackplane).name)));
[rr,cc]=size(equatorim);
Sphere=zeros(rr,cc,ff);

for ii=1:ff
    Sphere(:,:,ii)=...
    double(imread(strcat(inpth,insubdir,tiflist(ii).name)));
end

Rz=equator-southpole;
Tropics=Sphere(:,:,equator-5:equator+5);
trackim=sum(Tropics,3);
trackim(trackim>0.3*max(trackim(:)))=0.3*max(trackim(:)); %crop

%Get center and radius via VanLoenHoutQiTracker
if ~manualclick
QI=TrackXY_by_QI_Init(trackim);
[xnw,ynw,Qiprofs]=TrackXY_by_QI(trackim,QI,0);
RadialProfile=sum(Qiprofs);
[~,Nsamples]=max(RadialProfile);
Rxy=Nsamples/QI.radialoversampling;
else
    P_Color(trackim,cc,rr,'hot'); axis equal; axis tight; hold on
    [x,y,but]=ginput(2);
    xnw=x(1);     ynw=y(1);
    Rxy=((x(1)-x(2)).^2+(y(1)-y(2)).^2).^0.5;
end

%flip the sphere
FlipSphere=shiftdim(Sphere,flipit);  %Zaxis is second

%setup polar coordinates; note z correction
thetaax=linspace(0,-pi,180);  %note units of degree
phiax=linspace(0,2*pi,360);
rrax=linspace(Rxy-skindepth, Rxy+skindepth,2*skindepth+1);
[Thetas,Phis,Radii]=meshgrid(thetaax,phiax,rrax);


switch flipit
    case 1
    SamplingGridXX=(Rz/Rxy)*Radii.*sin(Thetas).*sin(Phis)+equator;
    SamplingGridYY=Radii.*sin(Thetas).*cos(Phis)+xnw;
    SamplingGridZZ=Radii.*cos(Thetas)+ynw;  %
    case 2
    SamplingGridYY=(Rz/Rxy)*Radii.*sin(Thetas).*sin(Phis)+equator;
    SamplingGridXX=Radii.*sin(Thetas).*cos(Phis)+xnw;
    SamplingGridZZ=Radii.*cos(Thetas)+ynw;  %
end

figure;
plot3(SamplingGridXX(1:5:end,1:5:end,1),SamplingGridYY(1:5:end,1:5:end,1),SamplingGridZZ(1:5:end,1:5:end,1),'o-');

[rrf,ccf,fff]=size(FlipSphere);
[XX,YY,ZZ]=meshgrid(1:ccf,1:rrf,1:fff);
SphereSampling=interp3(XX,YY,ZZ,FlipSphere,SamplingGridXX,SamplingGridYY,SamplingGridZZ);

FanalistaWorld=sum(SphereSampling,3);
%plot result of radial tracking


%plot menu
figure;
ccx=xnw+Rxy*cos(phiax); ccy=ynw+Rxy*sin(phiax);
pcolor(trackim); shading flat; colormap hot; axis equal; axis tight; hold on
plot(ynw,xnw,'bx', 'MarkerSize',10); hold on;
plot(ccy,ccx,'b-');
title('equator,center-tracked')
figure;
pcolor(FanalistaWorld'); shading flat, colormap hot; axis equal; axis tight
nme=strcat('surfacemap-skin-',num2str(skindepth),insubdir(1:end-1));
title(nme);


saveas(gcf, [inpth nme '.jpg']);

