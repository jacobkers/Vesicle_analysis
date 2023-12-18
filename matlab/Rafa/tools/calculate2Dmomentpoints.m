function [xm,ym,theta,ecc]=JKD2_XY_calculate2Dmomentpoints(points,weigh);
%Central angular moment of a collection of points (X,Y,I)
%'I' can serve as weight of not
%from: http://en.wikipedia.org/wiki/Image_moment
%JacobKers 2012

if nargin<2  %DEMO Mode: random collection of points with intensity increasing with x and y
    weigh=1;
    n=1000;    
    x=rand(n,1);
    y=rand(n,1);
    I=x.*y;   %to add assymmetry
    points=[x y I];
end

    x=points(:,1);
    y=points(:,2);
    I=points(:,3);

    
 if ~weigh,
     I=0*I+1;
 end
     

%raw moments M_ij of points: Mij=sum(x^i*y^j*Ixy)
M00=sum(sum(I));
M10=sum(sum(x.*I));
M11=sum(sum(y.*x.*I));
M01=sum(sum(y.*I));
M20=sum(sum(x.^2.*I));
M02=sum(sum(y.^2.*I));

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

%---------------------------------------------------------------
%now, theta can be either perpendicular or parallel to all points.
%to check, we calculate the cumulative distance of the points to the line given by xm,ym and theta:
k2=tan(theta*pi/180); 
k1=-1/k2;  %perpendicular slope

xc1=((y-ym)+k1*xm-k2*x)/(k1-k2); 
yc1=ym+k1*(xc1-xm); 
dist1=sum((x-xc1).^2+(y-yc1).^2).^0.5;  
%
xc2=((y-ym)+k2*xm-k1*x)/(k2-k1); 
yc2=ym+k2*(xc2-xm); 
dist2=sum((x-xc2).^2+(y-yc2).^2).^0.5;  
%
thets=[theta+90 theta];
dists=[dist1 dist2]; [~,idx]=min(dists); theta=thets(idx);

 
 if nargin<2
     close all;
     plot(x,y, 'o'); hold on; axis square
     plot(xm,ym,'ro', 'MarkerSize',10, 'MarkerFaceColor', 'r');
 end

