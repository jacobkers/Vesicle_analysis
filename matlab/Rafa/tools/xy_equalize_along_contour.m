function [xn,yn]=xy_equalize_along_contour(x00,y00,pts)
%This function takes a 2D-contour [x,y] and resamples it such that new points
%lie at interpolated positions between the old ones, but at approxmately equal distances
%measured along this contour, to conserve sharp bends)

if nargin<3 %Demo mode on a sine with non-equally spaced points
    pts=100;
    close all;
    imsz=100;
    pts=10;
    x0=linspace(1,100,pts)'; %equal axis
    x00=(x0/imsz).^3*imsz;   
    y00=imsz/2*(1+0.25*rand(pts,1))+imsz/3*sin(x00/imsz*2*pi);   
end
xn=x00;
yn=y00;
%pts=expandit*length(xn);

for k=1:3;   
    x=xn;
    y=yn;
    %first, measure contour length; determin average distance between points
    CL=sum(((x(2:end)-x(1:end-1)).^2+...
            (y(2:end)-y(1:end-1)).^2).^0.5);  %approximate contour length
    dst=CL/(pts-1) ;     
    lx=length(x); 
    xn=x(1);  
    yn=y(1);  
    li_tot=0;
    li_buf=0;
    c=1;
    substps=25;
    for i=1:lx-1    
        xip=linspace(x(i),x(i+1),substps);
        yip=linspace(y(i),y(i+1),substps);
        for j=1:substps-1
            di=((xip(j+1)-xip(j)).^2+(yip(j+1)-yip(j)).^2).^0.5;
            li_buf=li_buf+di;  % length
            if li_buf>=dst  %keep the point 
                li_buf=li_buf-dst;
                xn=[xn; xip(j)];
                yn=[yn; yip(j)];
               
            end  
        end   
    end
end

% %forces cropping (for rounding effects)
% xn=xn(1:pts);
% yn=yn(1:pts);

    if nargin<2 %Demo mode on a sine with non-equally spaced points
        plot(x00,y00,'o-'); hold on;
        plot(xn,yn,'ro-');
    end
    
   
    