function [pore_inner_rim,masked_inner_pore]=get_rim_by_radial_edge(area,area_mask);
%get edge of area by radial edge finding

%% sobel edge filter
area=1000*area/max(area(:));
[area_sobel Mx My]= GSobel(area,5);
area_sobel=1000*area_sobel/max(area_sobel(:));
QI=TrackXY_by_QI_Init(area_mask);
[xnw,ynw]=TrackXY_by_QI(area_sobel,QI,0);

%% get polar sampling grid
Xsamplinggrid=QI.X0samplinggrid+xnw;
Ysamplinggrid=QI.Y0samplinggrid+ynw;
       
%% combine edge enhancement with level of pore
% both were %normalized before, weighted here
wgt1=1; wgt2=0.2;
area_smz=matrix_blur_jk(area,3);
work_image=(wgt1*area_sobel+wgt2*area_smz).*area_mask;
allprofiles=(interp2(work_image,Xsamplinggrid,Ysamplinggrid,'NaN'));
allprofiles_smz=matrix_blur_jk(allprofiles,3);
[rr,cc]=size(allprofiles);
      
%% apply temporal semi-periodic expansion
[aa,r0]=size(allprofiles);
paddit=round(aa/4);
allprofiles_expanded=[allprofiles_smz(end-paddit:end,:); allprofiles_smz ; allprofiles_smz(1:paddit,:)];
hf=10;
[aa2,r0]=size(allprofiles_expanded);
cnt=0;

%% find ring
for ai=hf+1:aa2-hf
   cnt=cnt+1;
   ai_padd=ai+paddit;
   prf=(nanmean(allprofiles_expanded(ai-hf:ai+hf,:)));  
    %this is the averaged cross-profile
    %get main props:
   [val,ix]=max(prf);
   r_rim_rw(cnt)=ix;
   dum=1;
end 


r_rim_cln=clean_rim(r_rim_rw,hf);
ax_exp=1:length(r_rim_cln);

pts=[ax_exp' r_rim_cln', 0*ax_exp'+1];


% re-cut section matching original angle axis:
r_rim_cln=r_rim_cln(paddit-hf+1:end-paddit+hf-1);       
ax=ax_exp(paddit-hf+1:end-paddit+hf-1);


if 0
    figure;    
    pcolor(allprofiles_expanded); colormap bone; shading flat; hold on;        
    plot(r_rim_rw,ax_exp,'r-o');
    plot(r_rim_cln,ax,'w-', 'LineWidth', 2);
    [~]=ginput(1);
    close(gcf);
end

%% construct smooth contour:
[pore_inner_rim,masked_inner_pore]=build_inner_mask(area,QI,r_rim_cln,xnw,ynw);
 
