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
            
            [rim,mask]=get_rim_by_radial_edge(band_msk.*roi_gr,roi_msk);
            
            if 1
                pcolor(band_msk.*roi_gr);  shading flat, colormap hot, hold on;
                plot(rim.x,rim.y, 'w-', 'LineWidth', 2);
                pause(0.1);
                if mod(fri,20)==0, close(gcf); end
                %[~]=ginput(1);
            end
            dum=1;
    end
end
 
function [roi_gr, roi_re, roi_msk]=get_rois(all_frames,roidata, frame_index,roi_index,init)
    %get props: 
    xi=roidata.X(roi_index)+roidata.Width(roi_index)/2;  %corner point plus half-width
    yi=roidata.Y(roi_index)+roidata.Height(roi_index)/2;  %analogous
    Ri=roidata.Width(roi_index)/2; % app.radius
    area_pixels=all_frames(frame_index).roi(roi_index).props.PixelIdxList;
               
    %get FOVs:
    im_gr=imread([init.exp_path,init.filename_green], frame_index);
    im_re=imread([init.exp_path,init.filename_red], frame_index);
    im_msk=0*im_gr; 
    im_msk(area_pixels)=1;
       
    %ImageJ-based pre-masking and cropping of FOVs, BW:
    [rr,cc]=size(im_gr);
    [XX,YY]=meshgrid(1:cc,1:rr);
    lox=max([1, xi-Ri]); hix=min([cc, xi+Ri]);                              
    loy=max([1, yi-Ri]); hiy=min([rr, yi+Ri]); 
    RR=((XX-xi).^2+(YY-yi).^2).^0.5;
    im_gr(RR>Ri)=0; 
    im_re(RR>Ri)=0;
    roi_gr=double(im_gr(loy:hiy, lox:hix));
    roi_re=double(im_re(loy:hiy, lox:hix));
    roi_msk=double(im_msk(loy:hiy, lox:hix));
