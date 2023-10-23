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