function [xm,ym,theta,ecc]=TrackXY_by_COM_2Dmoment(im)
%JWJK: Central angular moment of a picture
%from: http://en.wikipedia.org/wiki/Image_moment
%Jacob Kerssemakers
%:JWJK-------------------------------------

if nargin<1  %DEMO mode
    close all;
    r=10;
    c=20;
    [x,y]=meshgrid(1:c,1:r);
    ofs=0;
    ec=2;   %separation of spots 
    x0=1*ec/2+c/2+ofs;
    y0=0*ec/2+r/2+ofs;
    x1=1*-ec/2+c/2+ofs;
    y1=0*-ec/2+r/2+ofs;
    sig=1.5;
    r0=((x-x0).^2+(y-y0).^2).^0.5; %'radial picture'
    r1=((x-x1).^2+(y-y1).^2).^0.5; %'radial picture'
    im=exp(-(r0/sig).^2)+exp(-(r1/sig).^2)+0.1*exp(-((y-r/2)/r).^2);
    im=(im-min(min((im)))).^4;    
else
    [r,c]=size(im);
    [x,y]=meshgrid(1:c,1:r);
end%-------------------------------------------------------


im=abs(im-median(im(:)));

%raw moments M_ij of matrix: Mij=sum(x^i*y^j*Ixy)
M00=sum(sum(im));
M10=sum(sum(x.*im));
M11=sum(sum(y.*x.*im));
M01=sum(sum(y.*im));
M20=sum(sum(x.^2.*im));
M02=sum(sum(y.^2.*im));

%Centroid row 
xm=M10/M00; 
%Centroid column 
ym=M01/M00;

%Second order central moments
mu_prime20=M20/M00-xm^2;
mu_prime02=M02/M00-ym^2;
mu_prime11=M11/M00-xm*ym;

theta=0.5*atan(2*mu_prime11/(mu_prime20-mu_prime02))*180/pi;

%eigenvalues covariance matrix:
labda1=0.5*(mu_prime20+mu_prime02)+0.5*(4*mu_prime11^2+(mu_prime20-mu_prime02)^2)^0.5;
labda2=0.5*(mu_prime20+mu_prime02)-0.5*(4*mu_prime11^2+(mu_prime20-mu_prime02)^2)^0.5;
%eccentricity
ecc=(1-labda2/labda1)^0.5;

% xm
% ym
% theta
% ecc

%close all; figure; pcolor(im); colormap hot; shading flat; axis equal; 
%[~]=ginput(1); close(gcf);
if nargin<1
    pcolor(im); shading flat; colormap hot; hold on;
    plot(xm,ym,'wo', 'MarkerSize', 10);
end
