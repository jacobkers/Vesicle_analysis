
function blur_matrix=matrix_blur_jk(matrixdata,w);
%blur a 2D matrix. borders are replicated; sum of pixels is preserved
%JacobKers 2013
if nargin<2
w=10;
matrixdata=ones(200,200);
matrixdata(50:150,50:150)=10;
end

sumI=nansum(matrixdata(:));

%make a kernel image
[X,Y]=meshgrid(1:6*w,1:6*w);
[r,c]=size(X);
R=((X-c/2).^2+(Y-r/2).^2).^0.5;
blur_kernel=(2^32-1)*exp(-(R.^2/w^2))./sum(sum(exp(-(R.^2/w^2)))); % make a gaussian blob kernel
blur_kernel=blur_kernel/sum(blur_kernel(:));
scale=100;
m1=round(matrixdata*scale);
im = uint32(round(m1' - 1));
blur_im=imfilter(im, blur_kernel,'replicate');
blur_matrix=(double(blur_im)+1)';

sumblurI=nansum(blur_matrix(:));
blur_matrix=blur_matrix/sumblurI*sumI;

if nargin<2
figure;
    subplot(1,2,1); pcolor(matrixdata); shading flat; colormap bone; hold on
    title('''JKD2 IM SmoothJK'' DEMO');
    subplot(1,2,2); pcolor(blur_matrix); shading flat; colormap bone; hold on
    blur_matrix=1;
    
end
