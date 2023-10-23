function [area_inner_rim ,masked_area]=build_inner_mask(pore,QI,r_rim,xnw,ynw)  %get radius and angle back
%JWJK_C:---------------------------------------------------------------
%Description: build a mask from rim data
%Input: pore picture, rim data, style
%'hardmask': build binary mask by filling rim
%'softmask': build mask with sofene edge
%Output:  mask and rim xy coordinates
%References: written by Jacob Kers, 2020
%:JWJK_C-------------------------------------------------------------------

       %build radial softfill mask
       %for every angle, set radial profile
       %sample calc R&aa from XXY, YY.; interpolate from radial plot
       
       %common: make cleaned xy contour from radial coordinates
       rimfit=round(r_rim); 
       innerrimrad=QI.radbii(rimfit);
       innerrimangle=QI.angles';
       innerx1=xnw+innerrimrad.*cos(innerrimangle);
       innery1=ynw+innerrimrad.*sin(innerrimangle);  
       aa=length(rimfit);
       [pore_inner_rim_x,pore_inner_rim_y]=xy_get_smooth_xyline(innerx1,innery1,aa,15);
       rx=round(pore_inner_rim_x);
       ry=round(pore_inner_rim_y);
         
       %build mask
       masked_area=0*pore;
       [rr,cc]=size(masked_area);
       [XX,YY]=meshgrid(1:rr,1:cc);
             
        %check
        [rr,cc]=size(masked_area);
       rx(rx<=0)=1;
       ry(ry<=0)=1;
       rx(rx>cc)=cc;
       ry(ry>rr)=rr;
       
       for ii=1:length(rx);
            masked_area(ry(ii),rx(ii))=1;
       end
       masked_area=bwmorph(masked_area,'dilate',2); %close
       masked_area = imfill(masked_area, 'holes');
       masked_area=bwmorph(masked_area,'erode',2); %shrink
        area_inner_rim.x=pore_inner_rim_x;
        area_inner_rim.y=pore_inner_rim_y;
        area_inner_rim.xc=xnw;
        area_inner_rim.yc=ynw;