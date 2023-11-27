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
    N_chan=length(init.chan_suffixes);
    frame_line=zeros(ff,1);
    area=zeros(ff,1);
    contour_length=zeros(ff,1);
    circularity=zeros(ff,1);
    axis_ratio=zeros(ff,1);
    fit_bri=zeros(ff,N_chan); 
    for fri=1:init.skips:ff
           disp(['roi' num2str(roi_i) 'frame' num2str(fri)]);
            %% get basic properties per frame
            frame_line(fri)=fri;
            area(fri)=all_frames(fri).roi(roi_i).props.Area;
            circularity(fri)=all_frames(fri).roi(roi_i).props.Circularity;
            axis_ratio(fri)= all_frames(fri).roi(roi_i).props.MajorAxisLength/...
                        all_frames(fri).roi(roi_i).props.MinorAxisLength;
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
            plot_msk=band_msk.*roi_ref;
               
            %find flexible edge via the ref channel:
            [rim,mask]=get_rim_by_radial_edge(band_msk.*roi_ref,roi_msk);
            map_ax=1:length(rim.x);
            contour_length(fri)=round(sum((...
                (rim.x(2:end)-rim.x(1:end-1)).^2+...
                (rim.y(2:end)-rim.y(1:end-1)).^2).^0.5));  
            
            %get mapping grid:                    
            rimwidth_sampling=[7 7];  %outer inner 
            [contour_map_ref, xxip, yyip]=xy_sample_grid_around_contour(roi_ref, rim.x, rim.y ,rimwidth_sampling);
            
            %map all channels:
            for chi=1:N_chan
                roi=roi_st(:,:,chi);
                %sample ring map:
                [contour_map, ~,~]=xy_sample_grid_around_contour(roi, rim.x, rim.y ,rimwidth_sampling);
                %get contour 1D props:
                sumprofile=sum(contour_map);
                widths=get_map_profiles(contour_map);
                %get acceptable sections (keep lengths)
                accept_idx=find(widths<2.8);
                map_ax_acc=map_ax(accept_idx);
                sumprofile_acc=sumprofile(accept_idx);
                widths_acc=widths(accept_idx);
                map_sum_fit=polyval(polyfit(map_ax_acc-mean(map_ax),sumprofile_acc,5),map_ax-mean(map_ax));
                fit_bri(fri,chi)=max(map_sum_fit);
                
                % some per_frame_plotting:
                if 0 % 0& circularity(fri)<0.7
                    subplot(4,N_chan,chi);
                        pcolor(roi);  shading flat, axis equal, axis tight, colormap hot, hold on;
                        plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
                        plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);
                        title(init.chan_suffixes{chi});
                    subplot(4,2,chi+2);
                        pcolor(contour_map);  axis tight, shading flat,  colormap hot, hold on;                               
                    subplot(4,N_chan,chi+4);
                        plot(map_ax,sumprofile, 'o');  axis tight; hold on;
                        plot(map_ax,map_sum_fit, 'r-'); hold off;
                        xlim([0 length(rim.x)]);
                        ylabel('content/length, a.u.');  
                    subplot(4,2,chi+6);
                        plot(map_ax,widths, 'k-');  axis tight,
                        xlim([0 length(rim.x)]);
                        ylabel('fwhm, pixels');
                pause(0.3);
                if mod(fri,20)==0, close(gcf); end
                end     
            end
            
         
            %reject budding or otherwise perturbed sections  
            
            
            %plot per frame, per channel     
            dum=1;
    end
    
    %% save and plot
    OutName=['A25_outdata_ROI', num2str(roi_i)];
    if ~isdir(init.savepath), mkdir(init.savepath); end
    
    %% wrap up jpg:
    close all;
    figure(123);
        ref_id=init.chan_ref_id;
        roi_ref=roi_st(:,:,ref_id);
    subplot(2,4,1);
       pcolor(roi);  shading flat, axis equal, axis tight, colormap hot, hold on;
       plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
       plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);   
       title(['roi' num2str(roi_i), '-last frame']);
    subplot(2,4,2);
        plot(frame_line, area, 'ko', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('area (pixels)');
        title('area');
    subplot(2,4,3);
        plot(frame_line, axis_ratio, 'mo', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('ratio (a.u.))');
        title('axis ratio');
    subplot(2,4,4);
        plot(frame_line, contour_length, 'bo', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('length (pixels)');
        title('contour length');
    for chi=1:N_chan
    subplot(2,4,4+chi);
        plot(frame_line, fit_bri(:,chi), 'go', 'MarkerSize',2);
        xlabel('frame index');
        ylabel('intensity (a.u.)');
        title(['brightness' init.chan_suffixes{chi}];
        ylim([0 1000]);
    end
    saveas(gcf,[init.savepath,OutName, '.jpg']);
              
    %excel:
    OutData=[frame_line area circularity contour_length fit_bri];
    ColNames=[{'frame'}, {'area (pixels)'},{'circularity'},...
             {'contour_length (pixel units)'} , ...
             init.chan_suffixes];   
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
    
    
    