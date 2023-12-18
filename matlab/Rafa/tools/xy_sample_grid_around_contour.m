function [contour_map, xxip, yyip]=xy_sample_grid_around_contour(image, fx, fy ,hw)
%Build an interpolation grid pependicular to a filament-----------------------------------------
%First, define perpendicular directions for the filament

lf=length(fx);
stripwidth=hw(1)+hw(2)+1;
stepvector=[-hw(1):hw(2)]';
xxip=zeros(stripwidth,lf);
yyip=zeros(stripwidth,lf);
dx=fx(2:end)-fx(1:end-1); 
dx=[dx(1) dx dx(end)]';
dy=fy(2:end)-fy(1:end-1); 
dy=[dy(1) dy dy(end)]';
tng=atan2(dy,dx); 
prp=atan2(-dx,dy);
%Then, build a grid from this
for i=1:lf
    xxip(:,i)=fx(i)+cos(tng(i)+pi/2)*(stepvector);
    yyip(:,i)=fy(i)+sin(tng(i)+pi/2)*(stepvector);
end

ipgridx=xxip;
ipgridy=yyip;

contour_map=interp2(image,ipgridx,ipgridy,'NaN');