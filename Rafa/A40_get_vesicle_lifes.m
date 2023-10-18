function A40_get_vesicle_lifes(init)
close all;
load([init.savepath, 'areadata.mat']);

QI=TrackXY_by_QI_Init(double(first_im));
[xnw,ynw,Qiprofs, allprofiles]=TrackXY_by_QI(double(first_im),QI,1);
RadialProfile=sum(Qiprofs);
[~,Nsamples]=max(RadialProfile);
Rxy=Nsamples/QI.radialoversampling;
figure;
    pcolor(allprofiles'); 
    title('vesicle map');
    xlabel('angular position, a.u.')
    ylabel('radial position, a.u.')
    shading flat

%plot properties over time
[~,ff]=size(all_areas);
[N_guvs,~]=size(all_areas(1).this_image);
figure;
    subplot(2,3,1); pcolor(first_im); shading flat, colormap jet; axis equal; axis tight
    title('first frame');
    subplot(2,3,4); pcolor(example_im); shading flat, colormap jet; axis equal; axis tight
    title('detected');
    subplot(1,3,2);
    for guv_id=1:N_guvs
        %build any property
        frame_line=[];
        property1=[];
        property2=[];
        for fri=1:ff
            guv_pointer=Guv_list(fri,guv_id);
            if ~isnan(guv_pointer)
                frame_line(fri)=fri;
                property1(fri)=all_areas(fri).this_image(guv_pointer).Area;
                property2(fri)=all_areas(fri).this_image(guv_pointer).Circularity;
            end
        end
        subplot(1,3,2);     plot(frame_line, property1, 'o-'); hold on;
        title('areas');
        xlabel('frame');
        ylabel('area, pixels');
        ylim([0 10000]);
        subplot(1,3,3);     plot(frame_line, property2, 'o-'); hold on;
        title('circularity');
        ylim([0 1.5]);
        xlabel('frame');
        ylabel('area, pixels');
        dum=1;
    end