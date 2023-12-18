function fil_im=filament_it(image,points);
%% 
%Build a 'filament' image from a collection of detected points; 
%This is done by point for point:
%1) select a cluster of nearby points; calculate 2D moment direction & COM
%position
%2) by adding a elliptical Gaussian spot according to location and
%direction
%3 All Gaussians added yields a smooth pattern enhancing filaments

%for other tools
cur_pth=pwd; cd .., addpath(genpath(pwd)); cd(cur_pth);

L_ax=20;  %long axis of gaussian
S_ax=5;   %short axis of gaussian
SearchRadius=2*L_ax; %radius of points to use
W_sq=L_ax;  %area to add signal (saves time)

if nargin<2;  %TEST MODE    
    imsz=500;
    pts=200;
    image=ones(500,500);
    x=linspace(10,imsz-10,pts)';
    y=imsz/2*(1+0.25*rand(pts,1))+imsz/3*sin(x/imsz*2*pi);
    I=rand(pts,1);
    points=[x y I];
end

    ls=length(points);
    [r,c]=size(image);
    fil_im=0*image;
    [xfr,yfr]=meshgrid(1:c,1:r);                   
    x=points(:,1); y=points(:,2); I=points(:,3);  
    for j=1:ls       
       x0=points(j,1); y0=points(j,2); r0=SearchRadius;     
       nearpoints=get_near_points(x0,y0, r0, points);
       %if enough points, calculate angular moment: 
       if length(nearpoints(:,1))>2              
           [xm,ym,theta,ecc]=calculate2Dmomentpoints(nearpoints,1);          
           theta2=90+theta;
           %use the eccentricity as a weight
           if ecc>0.3  %linear feature
                fil_im=add_ellipsoid_gaussian(fil_im,xfr,yfr,xm,ym,theta,ecc,L_ax,S_ax,W_sq);
           else  % symmetric feature, do not choose a direction
                fil_im=add_ellipsoid_gaussian(fil_im,xfr,yfr,xm,ym,theta,ecc,L_ax,L_ax,W_sq);
           end
       end
    end
    
    if nargin<2;  %TEST MODE
        close all;
        pcolor(fil_im); shading flat; colormap hot, hold on;
        plot(x,y,'w*');
        title('''JK2D IM Filament it'' DEMO RESULT');
    end
   

function picout=add_ellipsoid_gaussian(picin,x,y,x0,y0,thetadeg,eccweight,sig1,sig2,work_sq);
%Add a rotated elliptical spot
picout=picin;
    theta=thetadeg*pi/180;
    [r,c]=size(picin);
    xc=x-x0;
    yc=y-y0;
    %select a square of local coordinates
    sel=find((abs(xc)<=work_sq)&...
             (abs(yc)<=work_sq));   
    %avoid edges
    pixelarea=length(sel);
    if pixelarea==(2*work_sq)^2  
        lox=min(x(sel));
        hix=max(x(sel));
        loy=min(y(sel));
        hiy=max(y(sel));
        %local coordinates       
        subx=xc(sel); subx = reshape(subx,2*work_sq,2*work_sq);
        suby=yc(sel);  suby = reshape(suby,2*work_sq,2*work_sq); 
        %rotated local coordinates
        rotx=subx*cos(theta)+suby*sin(theta);
        roty=-subx*sin(theta)+suby*cos(theta);
        picout(loy:hiy,lox:hix)=picin(loy:hiy,lox:hix)+eccweight*exp(-((rotx/sig1).^2+(roty/sig2).^2));
    end     
     
    function nearpoints=get_near_points(x0,y0, r0, points)
    %this function returns  coordinates within a distance r0 from a point x0,y0 in a 'peaks'(x,y,I,) database
    %JacobKers 2012
    rall=((points(:,1)-x0).^2+(points(:,2)-y0).^2).^0.5;
    %sel=find(rall<r0);                
    nearpoints=points(rall<r0,:);
        