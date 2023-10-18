function A40_get_vesicle_lifes(init)
close all;
load([init.savepath, 'areadata.mat']);
[rr,cc]=size(first_im);
[XX,YY]=meshgrid(1:cc,1:rr);
roidata=readtable([init.exp_path, init.filename_rois]);
pos_xx=roidata.X+roidata.Width/2;  %corner point plus half-width
pos_yy=roidata.Y+roidata.Height/2;  %analogous
pos_rr=roidata.Width/2; % app.radius
N_rois=length(pos_xx);


%plot properties over time
[~,ff]=size(all_frames);
figure;
    subplot(2,3,1); pcolor(first_im); shading flat, colormap jet; axis equal; axis tight
    title('first frame');
    subplot(2,3,4); pcolor(example_im); shading flat, colormap jet; axis equal; axis tight
    title('detected');
    subplot(1,3,2);
    for roi_i=2:N_rois
        %build any property
        frame_line=[];
        property1=[];
        property2=[];
        for fri=1:ff
                %collect the property of interest from earlier analysis
                frame_line(fri)=fri;
                property1(fri)=all_frames(fri).roi(roi_i).props.Area;
                property2(fri)=all_frames(fri).roi(roi_i).props.Circularity;
                
                %load the image for extra analysis
                im_gr=imread([init.exp_path,init.filename_green], fri);
                im_re=imread([init.exp_path,init.filename_red], fri);
                xi=pos_xx(roi_i);
                yi=pos_yy(roi_i);
                Ri=pos_rr(roi_i);
                lox=max([1, xi-Ri]); hix=min([cc, xi+Ri]);                              
                loy=max([1, yi-Ri]); hiy=min([rr, yi+Ri]); 
                RR=((XX-xi).^2+(YY-yi).^2).^0.5;
                im_gr(RR>Ri)=0; 
                im_re(RR>Ri)=0;
                roi_gr=im_gr(loy:hiy, lox:hix);
                roi_re=im_re(loy:hiy, lox:hix);
                QI=TrackXY_by_QI_Init(roi_gr);
                [~,~,~, map_gr]=TrackXY_by_QI(double(roi_gr),QI,0);
                [~,~,~, map_re]=TrackXY_by_QI(double(roi_re),QI,0);

    
                figure(41);
                subplot(2,2,1), pcolor(roi_gr); shading flat, axis equal
                subplot(2,2,2), pcolor(roi_re); shading flat, axis equal
                subplot(2,2,3), pcolor(map_gr'); shading flat
                    title('vesicle map');
                    xlabel('angular position, a.u.')
                    ylabel('radial position, a.u.')
               subplot(2,2,4), pcolor(map_re'); shading flat
                    title('vesicle map');
                    xlabel('angular position, a.u.')
                    ylabel('radial position, a.u.')
    
                pause(0.5);
                [~]=ginput(1);
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
    
 if 0   
 
[xnw,ynw,Qiprofs, allprofiles]=TrackXY_by_QI(double(first_im),QI,1);
figure;
    pcolor(allprofiles'); 

 end