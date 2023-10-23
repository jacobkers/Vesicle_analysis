function sel=Get_local4max(im)
%This function finds the local four-neighbour maximum
[rr,cc]=size(im);
imt=im';
im_lft=im(2:end-1,1:end-2);
im_rgt=im(2:end-1,3:end);
im_mid=im(2:end-1,2:end-1);
im_top=im(1:end-2,2:end-1);
im_bot=im(3:end,2:end-1);
sel=find((im_lft<im_mid)&(im_rgt<im_mid)+...
         (im_top<im_mid)&(im_bot<im_mid))+1+rr;