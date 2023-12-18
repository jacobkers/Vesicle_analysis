function [lineX,lineY]=xy_get_smooth_xyline(lineX,lineY,pts,r0);
%this function starts out from a course line, and builds a
%smooth contour from these points

[lineX,lineY]=xy_sort_contour(lineX,lineY);    
    
%equalize and iterpolate   
[lineX,lineY]=xy_equalize_along_contour(lineX,lineY,pts); 
%smooth
[lineX,lineY]=xy_get_smooth_line_by_com(lineX,lineY,r0);


if nargin <2
    close all;
    pcolor(BWedge); shading flat; colormap bone; hold on;  
    plot(lineX,lineY,'r-','Linewidth',2);        
end


