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
                area_pixels=all_frames(fri).roi(roi_i).props.PixelIdxList;
                %load the roi  for extra analysis
                im_gr=imread([init.exp_path,init.filename_green], fri);
                im_re=imread([init.exp_path,init.filename_red], fri);
                im_msk=0*im_gr; im_msk(area_pixels)=1;
                
                %user_roi masking:
                xi=pos_xx(roi_i);
                yi=pos_yy(roi_i);
                Ri=pos_rr(roi_i);
                lox=max([1, xi-Ri]); hix=min([cc, xi+Ri]);                              
                loy=max([1, yi-Ri]); hiy=min([rr, yi+Ri]); 
                RR=((XX-xi).^2+(YY-yi).^2).^0.5;
                im_gr(RR>Ri)=0; 
                im_re(RR>Ri)=0;
                roi_gr=double(im_gr(loy:hiy, lox:hix));
                roi_re=double(im_re(loy:hiy, lox:hix));
                %area masking:
                roi_msk=double(im_msk(loy:hiy, lox:hix));
                rimwidth=15;
                inner_roi_msk=bwmorph(roi_msk, 'erode', rimwidth);
                band_msk= roi_msk-inner_roi_msk;
                
                nan_msk=band_msk;
                nan_msk(nan_msk==0)=NaN;
                
                QI=TrackXY_by_QI_Init(roi_gr);
                %track center of red:
                [x_gre,y_gre,~, map_gr]=TrackXY_by_QI(double(roi_gr.*band_msk),QI,0);
                [x_re,y_re,~, map_re]=TrackXY_by_QI(double(roi_re.*band_msk),QI,0);
                %map mask green identically:
                Xsamplinggrid=QI.X0samplinggrid+x_gre;
                Ysamplinggrid=QI.Y0samplinggrid+y_gre;
                map_nan=(interp2(nan_msk,Xsamplinggrid,Ysamplinggrid,'NaN'));
                
                figure;
                pcolor((roi_gr/max(roi_gr(:)))+(roi_re/max(roi_re(:))));shading flat, axis equal
    
                figure(41);
                subplot(2,2,1), pcolor(roi_gr.*nan_msk); shading flat, axis equal
                subplot(2,2,2), pcolor(roi_re.*nan_msk); shading flat, axis equal
                subplot(2,2,3), pcolor((map_gr.*map_nan)'); shading flat
                    title('vesicle map');
                    xlabel('angular position, a.u.')
                    ylabel('radial position, a.u.')
               subplot(2,2,4), pcolor((map_re.*map_nan)'); shading flat
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