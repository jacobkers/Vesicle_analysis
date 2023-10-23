function [pore_inner_rim,masked_inner_pore]=get_rim_by_radial_edge(area,area_mask);
%Description: get edge of area by radial edge finding
%Input: pore picture
%Output:  rim data
%References: written by Jacob Kers, 2020
%:JWJK_C-------------------------------------------------------------------
%get center
%figure;
area=1000*area/max(area(:));
[area_sobel Mx My]= GSobel(area,5);
area_sobel=1000*area_sobel/max(area_sobel(:));
%sobel edge detction
QI=TrackXY_by_QI_Init(area_mask);
[xnw,ynw]=TrackXY_by_QI(area_sobel,QI,0);

%get polar sampling grid, use product of sobel and pore
Xsamplinggrid=QI.X0samplinggrid+xnw;
Ysamplinggrid=QI.Y0samplinggrid+ynw;
       
%we combine edge enhancement with level of pore, both were
%normalized before, weighted here
wgt1=1; wgt2=0.2;
area_smz=matrix_blur_jk(area,3);
work_image=(wgt1*area_sobel+wgt2*area_smz).*area_mask;
allprofiles=(interp2(work_image,Xsamplinggrid,Ysamplinggrid,'NaN'));
allprofiles_smz=matrix_blur_jk(allprofiles,3);
[rr,cc]=size(allprofiles);
      
%% find edge of inner rim using semi-periodic expansion
[aa,r0]=size(allprofiles);
paddit=round(aa/4);
allprofiles_expanded=[allprofiles_smz(end-paddit:end,:); allprofiles_smz ; allprofiles_smz(1:paddit,:)];
hf=10;
[aa2,r0]=size(allprofiles_expanded);
cnt=0;
for ai=hf+1:aa2-hf
   cnt=cnt+1;
   ai_padd=ai+paddit;
   prf=(nanmean(allprofiles_expanded(ai-hf:ai+hf,:)));
   [val,ix]=max(prf);
   r_rim_rw(cnt)=ix;
   dum=1;
end
       
%refine the profile, assuming it has a reasonably smooth form
r_rim_cln=Clean_rim(r_rim_rw,hf);

%section matching original angle axis:
ax_exp=1:length(r_rim_cln);
ax=ax_exp(paddit-hf+1:end-paddit+hf-1);
r_rim_cln=r_rim_cln(paddit-hf+1:end-paddit+hf-1);       

if 1
    figure; pcolor(allprofiles_expanded); colormap bone; shading flat; hold on;        
    plot(r_rim_rw,ax_exp,'r-o');
    plot(r_rim_cln,ax,'w-', 'LineWidth', 2);
    [~]=ginput(1);
end

[pore_inner_rim,masked_inner_pore]=BuildInnerMask(area,QI,r_rim_cln,xnw,ynw,'hardmask');
      
      function  r_rim=Clean_rim(r_rim,wndw);
%JWJK_C:---------------------------------------------------------------
%Description: this function removes far-outlying points (by radial
%position) as to get a smooth, semi-circular rim
%Input: rim data, window margin
%Output:  rim data
%References: written by Jacob Kers, 2020
%:JWJK_C-------------------------------------------------------------------
R0=nanmedian(r_rim);
[flag,cleanprf]=prf_outlier_flag(r_rim,3,0.5,'all',0);
R0_var=2*std(cleanprf);
bads=find((r_rim<(R0-R0_var))|r_rim>(R0+R0_var));
goods=find((r_rim>(R0-R0_var))&r_rim<(R0+R0_var));
lb=length(bads);
for jj=1:lb
   ib=bads(jj);
   [~,good_i]=min(abs(goods-ib));  %nearest good point
   replace_value=r_rim(goods(good_i));
   r_rim(ib)=replace_value;
end

if 0
   plot(r_rim); hold on;
   plot(50*flag);
end
dum=1;

%make smooth fit of rim
r_rim=(smooth(r_rim,wndw))';
dum=1;
      