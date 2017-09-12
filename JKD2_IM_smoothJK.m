
function blur_matrix=JKD2_IM_smoothJK(matrixdata,w);
%blur a 2D matrix. JacobKers2013

if nargin<2
w=10;
matrixdata=ones(200,200);
matrixdata(50:150,50:150)=10;
end

%make a kernel image
[X,Y]=meshgrid(1:6*w,1:6*w);
[r,c]=size(X);
R=((X-c/2).^2+(Y-r/2).^2).^0.5;
blur_kernel=(2^32-1)*exp(-(R.^2/w^2))./sum(sum(exp(-(R.^2/w^2)))); % make a gaussian blob kernel
blur_kernel=blur_kernel/sum(blur_kernel(:));
scale=(2^32-1)/max(matrixdata(:));
m1=round(matrixdata*scale);
im = uint32(round(m1' - 1));
blur_im=imfilter(im, blur_kernel,'replicate');
blur_matrix=(double(blur_im)+1)';

backscale=sum(matrixdata(:))/sum(blur_matrix(:));
blur_matrix=backscale*blur_matrix;

if nargin<2
figure;
    subplot(2,2,1); pcolor(matrixdata); shading flat; colormap bone; hold on
    title('''JKD2 IM SmoothJK'' DEMO');
    subplot(2,2,2); pcolor(blur_matrix); shading flat; colormap bone; hold on
    subplot(2,2,3); plot(matrixdata);
    subplot(2,2,4); plot(blur_matrix);
    blur_matrix=1;
    
end
