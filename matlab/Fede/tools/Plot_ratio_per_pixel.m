function Plot_ratio_per_pixel(initval);

[imlist_f,~]=Scroll_ImageDirs(initval.dir_FtsZ  ,'*.tif');
[imlist_z,~]=Scroll_ImageDirs(initval.dir_ZipA  ,'*.tif');

simbol=[{'rx'}, {'kx'}, {'bx'}];
legenda=[{'bottom'}, {'equator'}, {'top'}];
for ii=1:3
    fr=initval.bot_eq_top_planes(ii);
    im_f=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(fr).filname))),initval.smoothim);
    im_z=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_ZipA,imlist_z(fr).filname))),initval.smoothim);
    im_f=im_f-min(im_f(:));
    im_z=im_z-min(im_z(:));
    sel=Get_local4max(im_f);  %selects specific points
    figure(1)
    subplot(3,2,2*(ii-1)+1); pcolor(im_f); colormap bone, shading flat; axis equal, axis tight;
    axis off;
    title(char(legenda{ii}));
    subplot(3,2,2*(ii-1)+2); pcolor(im_z); colormap bone, shading flat; axis equal, axis tight;
    axis off;
    title(char(legenda{ii}));
    figure(2);
    plot(im_f(sel),im_z(sel), char(simbol{ii}), 'MarkerSize',3); hold on;
    title('intensity ratios');
    xlabel('FtsZ intesity, a.u');
    ylabel('ZipA intensity, a.u');
    legend(char(legenda));
end

