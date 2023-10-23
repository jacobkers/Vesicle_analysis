function A25_map_areas(init)
close all;
load([init.savepath, 'areadata.mat']);
[rr,cc]=size(first_im);
[XX,YY]=meshgrid(1:cc,1:rr);
roidata=readtable([init.exp_path, init.filename_rois]);
pos_xx=roidata.X+roidata.Width/2;  %corner point plus half-width
pos_yy=roidata.Y+roidata.Height/2;  %analogous
pos_rr=roidata.Width/2; % app.radius
N_rois=length(pos_xx);

[~,ff]=size(all_frames);
for roi_i=2:N_rois
    for fri=1:ff
            %collect basic properties
            frame_line(fri)=fri;
            property1(fri)=all_frames(fri).roi(roi_i).props.Area;
            property2(fri)=all_frames(fri).roi(roi_i).props.Circularity;
            area_pixels=all_frames(fri).roi(roi_i).props.PixelIdxList;
            
            %load the images  for extra analysis
            im_gr=imread([init.exp_path,init.filename_green], fri);
            im_re=imread([init.exp_path,init.filename_red], fri);
            im_msk=0*im_gr; im_msk(area_pixels)=1;

            %ImageJ-based pre-masking and cropping of red, green, BW:
            xi=pos_xx(roi_i);
            yi=pos_yy(roi_i);
            Ri=pos_rr(roi_i);  %
            lox=max([1, xi-Ri]); hix=min([cc, xi+Ri]);                              
            loy=max([1, yi-Ri]); hiy=min([rr, yi+Ri]); 
            RR=((XX-xi).^2+(YY-yi).^2).^0.5;
            im_gr(RR>Ri)=0; 
            im_re(RR>Ri)=0;
            roi_gr=double(im_gr(loy:hiy, lox:hix));
            roi_re=double(im_re(loy:hiy, lox:hix));
            roi_msk=double(im_msk(loy:hiy, lox:hix));
            
            %area masking:
            rimwidth=15;
            %inner mask:
            inner_roi_msk=bwmorph(roi_msk, 'erode', rimwidth);
            band_msk= roi_msk-inner_roi_msk;
            %nan_mask
            nan_msk=band_msk;
            nan_msk(nan_msk==0)=NaN;                        
    end
 end
