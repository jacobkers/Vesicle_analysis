function [roi_st, roi_ref, roi_msk]=get_rois(all_frames,roidata, frame_index,roi_index,init)
    %get props: 
    xi=roidata.X(roi_index)+roidata.Width(roi_index)/2;  %corner point plus half-width
    yi=roidata.Y(roi_index)+roidata.Height(roi_index)/2;  %analogous
    Ri=roidata.Width(roi_index)/2; % app.radius
    area_pixels=all_frames(frame_index).roi(roi_index).props.PixelIdxList;
               
    %get FOVs: 
    %one reference,
    source_ref=[init.exp_path,init.muscope_exportname,init.chan_suffixes{init.chan_ref_id}, '.tif'];
    im_ref=imread(source_ref, frame_index);
    [rr,cc]=size(im_ref);
    %small stack per channel
    N_chan=length(init.chan_suffixes);
    channel_stack=zeros(rr,cc,N_chan);
    for chi=1:N_chan
        source_chan=[init.exp_path,init.muscope_exportname,init.chan_suffixes{chi}, '.tif'];
        channel_stack(:,:,chi)=imread(source_chan, frame_index);
    end
    
    %build mask from reference:
    im_msk=0*im_ref; 
    im_msk(area_pixels)=1;
       
    %ImageJ-based pre-masking and cropping of FOVs, BW:
    [XX,YY]=meshgrid(1:cc,1:rr);
    lox=max([1, xi-Ri]); hix=min([cc, xi+Ri]);                              
    loy=max([1, yi-Ri]); hiy=min([rr, yi+Ri]); 
    roi_msk=double(im_msk(loy:hiy, lox:hix));
    roi_ref=double(im_ref(loy:hiy, lox:hix));
    
    [rrr,ccr]=size(roi_msk);
    roi_st=zeros(rrr,ccr,N_chan);
    %suppress%crop:
    RR=((XX-xi).^2+(YY-yi).^2).^0.5;
    for chi=1:N_chan
        buf=channel_stack(:,:,chi);
        buf(RR>Ri)=0;
        roi_st(:,:,chi)=buf(loy:hiy, lox:hix);
    end
    
    