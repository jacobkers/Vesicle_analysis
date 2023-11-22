function A25_map_areas(init)
%obtain properties per ROI and save them to self-describing excels
close all;
load([init.savepath, 'areadata.mat']);
[rr,cc]=size(first_im);
roidata=readtable([init.exp_path, init.filename_rois]);

N_rois=length(roidata.X);

[~,ff]=size(all_frames);
for roi_i=1:N_rois
    
    %set up
    
    frame_line=zeros(ff,1);
    area=zeros(ff,1);
    contour_length=zeros(ff,1);
    circularity=zeros(ff,1);
    fit_bri_gr=zeros(ff,1);
    fit_bri_re=zeros(ff,1);  
    skips=1; 
    for fri=1:skips:ff
           disp(['roi' num2str(roi_i) 'frame' num2str(fri)]);
            %% get basic properties per frame
            frame_line(fri)=fri;
            area(fri)=all_frames(fri).roi(roi_i).props.Area;
            circularity(fri)=all_frames(fri).roi(roi_i).props.Circularity;
            area_pixels=all_frames(fri).roi(roi_i).props.PixelIdxList;
                                   
            %% get rois:
            [roi_st, roi_ref, roi_msk]=get_rois(all_frames,roidata, fri,roi_i,init);
            
            %area masking:
            rimwidth_mask=5;
            %inner mask:
            inner_roi_msk=bwmorph(roi_msk, 'erode', rimwidth_mask);
            edge_msk=bwmorph(roi_msk, 'remove');
            band_msk=bwmorph(edge_msk, 'dilate', rimwidth_mask);
            
            %nan_mask
            nan_msk=1.0*band_msk;
            nan_msk(nan_msk==0)=NaN;
            plot_msk=band_msk.*roi_gr;
            
            %find flexible edge:
            [rim,mask]=get_rim_by_radial_edge(band_msk.*roi_ref,roi_msk);
            rimwidth_sampling=[7 7];  %outer inner 
            [contour_map_ref, xxip, yyip]=xy_sample_grid_around_contour(roi_gr, rim.x, rim.y ,rimwidth_sampling);
            
            
            %%%EDITED UP TO HERE
            
            
            
            [contour_map_re, ~,~]=xy_sample_grid_around_contour(roi_re, rim.x, rim.y ,rimwidth_sampling);
            
            %process 1-D contour properties
            contour_length(fri)=round(sum((...
                (rim.x(2:end)-rim.x(1:end-1)).^2+...
                (rim.y(2:end)-rim.y(1:end-1)).^2).^0.5));  
            %get profiles:
            map_ax=1:length(rim.x);
            map_sum_re=sum(contour_map_re);
            map_sum_gr=sum(contour_map_gr);
            
            map_width_re=get_map_profiles(contour_map_re);
            map_width_gr=get_map_profiles(contour_map_gr);
            
            med_re=median(map_width_re);
            med_gr=median(map_width_gr);
            
            %reject budding or otherwise perturbed sections            
            accept_idx_gr=find(map_width_gr<2.8);
            map_ax_gr=map_ax(accept_idx_gr);
            map_sum_gr=map_sum_gr(accept_idx_gr);
            map_width_gr=map_width_re(accept_idx_gr);
            
            accept_idx_re=find(map_width_re<2.8);
            map_ax_re=map_ax(accept_idx_re);
            map_sum_re=map_sum_re(accept_idx_re);
            map_width_re=map_width_re(accept_idx_re);
            
            %fit maximum:
            map_sum_re_fit=polyval(polyfit(map_ax_re-mean(map_ax_re),map_sum_re,5),map_ax-mean(map_ax_re));            
            map_sum_gr_fit=polyval(polyfit(map_ax_gr-mean(map_ax_gr),map_sum_gr,5),map_ax-mean(map_ax_gr));
            
            fit_bri_gr(fri)=max(map_sum_gr_fit);
            fit_bri_re(fri)=max(map_sum_re_fit);
            
            if 1 % 0& circularity(fri)<0.7
                subplot(4,2,1);
                    pcolor(roi_gr);  shading flat, axis equal, axis tight, colormap hot, hold on;
                    plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
                    plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);
                subplot(4,2,2);
                    pcolor(roi_re);  shading flat, axis equal, axis tight, colormap hot, hold on;
                    plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
                    plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);
                subplot(4,2,3);
                    pcolor(contour_map_gr);  axis tight, shading flat,  colormap hot, hold on;              
                subplot(4,2,4);
                    pcolor(contour_map_re);  axis tight, shading flat, colormap hot, hold on;                       
                subplot(4,2,5);
                    plot(map_ax_gr,map_sum_gr, 'o');  axis tight; hold on;
                    plot(map_ax,map_sum_gr_fit, 'r-'); hold off;
                    xlim([0 length(rim.x)]);
                    ylabel('content/length, a.u.');
                subplot(4,2,6);
                    plot(map_ax_re,map_sum_re, 'o');  axis tight, hold on;
                    plot(map_ax,map_sum_re_fit, 'r-'); hold off;
                    
                    xlim([0 length(rim.x)]);
                    ylabel('content/length, a.u.');
                subplot(4,2,7);
                    plot(map_ax_gr,map_width_gr, 'o');  axis tight,
                    xlim([0 length(rim.x)]);
                    ylabel('fwhm, pixels');
                subplot(4,2,8); 
                    plot(map_ax_re, map_width_re, 'o'); axis tight
                    xlim([0 length(rim.x)]);
                    ylabel('fwhm, pixels');
                pause(0.3);
                if mod(fri,20)==0, close(gcf); end
                % [~]=ginput(1);
            end
            dum=1;
    end
    
    %% save and plot
    OutName=['A25_outdata_ROI', num2str(roi_i)];
    if ~isdir(init.savepath), mkdir(init.savepath); end
    %jpg:
    close all;
    figure(123);
    subplot(2,3,1);
       pcolor(roi_gr);  shading flat, axis equal, axis tight, colormap hot, hold on;
       plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
       plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);   
       title(['roi' num2str(roi_i), '-last frame']);
    subplot(2,3,2);
        plot(frame_line, area, 'ko', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('area (pixels)');
        title('area');
    subplot(2,3,3);
        plot(frame_line, circularity, 'mo', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('circularity (a.u.))');
        title('circularity');
    subplot(2,3,4);
        plot(frame_line, contour_length, 'bo', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('length (pixels)');
        title('contour length');
    subplot(2,3,5);
        plot(frame_line, fit_bri_gr, 'go', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('intensity (a.u.)');
        title('brightness green');
        ylim([0 1000]);
    subplot(2,3,6);
        plot(frame_line, fit_bri_re, 'ro', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('intensity (a.u.)');
        title('brightness red');
        ylim([0 1000]);
    saveas(gcf,[init.savepath,OutName, '.jpg']);
              
    %excel:
    OutData=[frame_line area circularity contour_length fit_bri_gr fit_bri_re];
    ColNames=[{'frame'}, {'area (pixels)'},{'circularity'},...
             {'contour_length (pixel units)'} , ...
             {'green intensity'}, {'red intensity'}];   
    xlswrite([init.savepath,OutName, '.xlsx'], ColNames, 'Roidata','A1');
    xlswrite([init.savepath,OutName, '.xlsx'], OutData, 'Roidata', 'A2');
end
 

 function map_width=get_map_profiles(contour_map);
     [ww,L]=size(contour_map); 
     map_width=zeros(L,1);
     for ii=1:L
         prf=contour_map(:,ii);
         fwhm=get_FWHM_mainpeak(prf',1:ww);
         map_width(ii)=fwhm;
     end
     dum=1;
     
 function prf_fit=fit_expanded(ax,prf,order);
    xp=3;   
    order=order*xp;
    prf_fit=polyval(polyfit(1:xp*length(prf),repmat(prf,1,xp),order),length(prf)+1:length(prf));
    dum=1;
    
    
    