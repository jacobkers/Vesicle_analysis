function [xout,yout]=xy_get_smooth_line_by_com(xin,yin,r0);
%Smooth a collection of points and equalize them

if nargin<3;  %TEST MODE
    close all;
    imsz=500;
    pts=100;
    xin=linspace(imsz/10,imsz-imsz/10,pts)';
    yin=imsz/2*(1+0.3*rand(pts,1))+imsz/3*sin(xin/imsz*8*pi);
    r0=5;   
end
    ls=length(xin);                  

    for j=1:ls
       x0=xin(j); y0=yin(j);      
       [xnearpoints,ynearpoints]=get_near_points(x0,y0, r0, xin,yin);
       %if enough points, calculate angular moment: 
       nearpoints=[xnearpoints ynearpoints 0*xnearpoints];
       if length(nearpoints(:,1))>2              
           %plot(nearpoints(:,1),nearpoints(:,2), 'o'); hold on;
           [x1,y1,~,~]=xy_calculate2Dmomentpoints(nearpoints,0); 
       else 
           x1=x0;
           y1=y0;
       end
       xt(j)=x1;
       yt(j)=y1;
    end
    xt(1)=xin(1); yt(1)=yin(1);
    xt(end)=xin(end); yt(end)=yin(end);        
    xout=xt;
    yout=yt;  
    if nargin<3;  %TEST MODE
        close all;
        plot(xin,yin,'-o'); hold on; 
        plot(xout,yout,'-ro');
    end
    
    
    
function [xnearpoints,ynearpoints]=get_near_points(x0,y0, r0, xpoints, ypoints)
    %this function returns  coordinates within a distance r0 from a point x0,y0 in a 'peaks'(x,y,I,) database
    %JacobKers 2012
    rall=((xpoints-x0).^2+(ypoints-y0).^2).^0.5;
    %sel=find(rall<r0);                
    xnearpoints=xpoints(rall<r0);
    ynearpoints=ypoints(rall<r0);



        
        