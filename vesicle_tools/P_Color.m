function dum=P_Color(matrix,wo,ho, colmap)
%This function presents a workaround for the extremely annoying matlab bug:
%fail to refresh corsor crosshairs in 'pcolor' plots

outim=Deform_it(matrix,wo,ho);
pause(0.01);
imagesc(outim); colormap(colmap);
%imshow(outim); 
dum=1;
function outim=Deform_it(im,wo,ho);
%This function rescales an image in woxho blocks by 
%interpolation. 

[h,w]=size(im); 
outim=zeros(ho,wo);

grid_h=h/ho;
grid_w=w/wo;

%stepsize needed to get 'initval.hgt' gridlines in old image (can be larger or smaller than 1)
[XI,YI] = meshgrid(1:grid_w:w,1:grid_h:h);

buf=double(im)+1;  %R/G or B image
outim=interp2(im,XI,YI);
outim=outim/max(outim(:))*255;

outim = uint8(round(outim - 1));


function outim=Scale_it(im,w,h);
%This function scales an image via interpolation
%it needs an X and an Y scale. The smallest is taken.
%Jacob 6-1-2007
[sx,sy,rgb]=size(im); %sx=height!

step=max([sx/h sy/w]');
%stepsize needed to get 'initval.hgt' gridlines in old image (can be larger or smaller than 1)
[XI,YI] = meshgrid(1:step:sy,1:step:sx);

for i=1:rgb
buf=double(im(:,:,i))+1;  %R/G or B image
outbuf=interp2(buf,XI,YI);
outim(:,:,i)=outbuf;
end
outim = uint8(round(outim - 1));