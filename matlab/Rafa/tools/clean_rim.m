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