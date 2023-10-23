function A25_map_areas(init)
close all;
load([init.savepath, 'areadata.mat']);
[rr,cc]=size(first_im);
roidata=readtable([init.exp_path, init.filename_rois]);

N_rois=length(roidata.X);

[~,ff]=size(all_frames);
for roi_i=1:N_rois
    disp(roi_i)
    for fri=1:ff
            %% get basic properties
            frame_line(fri)=fri;
            property1(fri)=all_frames(fri).roi(roi_i).props.Area;
            property2(fri)=all_frames(fri).roi(roi_i).props.Circularity;
            area_pixels=all_frames(fri).roi(roi_i).props.PixelIdxList;
            
            %% get rois:
            [roi_gr, roi_re, roi_msk]=get_rois(all_frames,roidata, fri,roi_i,init);
            
            %area masking:
            rimwidth=5;
            %inner mask:
            inner_roi_msk=bwmorph(roi_msk, 'erode', rimwidth);
            edge_msk=bwmorph(roi_msk, 'remove');
            band_msk=bwmorph(edge_msk, 'dilate', rimwidth);
            
            %nan_mask
            nan_msk=1.0*band_msk;
            nan_msk(nan_msk==0)=NaN;
            plot_msk=band_msk.*roi_gr;
            
            %% find flexible edge 
            [rim,mask]=get_rim_by_radial_edge(band_msk.*roi_gr,roi_msk);
            
            [contour_map_gr, xxip, yyip]=xy_sample_grid_around_contour(roi_gr, rim.x, rim.y ,3);
            [contour_map_re, ~,~]=xy_sample_grid_around_contour(roi_re, rim.x, rim.y ,3);
            
            if 1
                subplot(1,2,1);
                    pcolor(roi_gr);  shading flat, axis equal, colormap hot, hold on;
                    plot(xxip(1,:),yyip(1,:), 'w-', 'LineWidth', 1);
                    plot(xxip(end,:),yyip(end,:), 'w-', 'LineWidth', 1);
                subplot(3,2,2);
                    pause(0.1);
                    pcolor(contour_map_gr);  
                    shading flat, colormap hot, axis equal; hold on;
                subplot(3,2,4);
                    pause(0.1);
                    plot(sum(contour_map_gr));  
                subplot(3,2,6);
                    pause(0.2);
                    plot(sum(contour_map_re));  
                if mod(fri,20)==0, close(gcf); end
                % [~]=ginput(1);
            end
            dum=1;
    end
end
 

