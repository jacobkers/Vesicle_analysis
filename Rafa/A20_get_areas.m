function A20_get_areas(init);
% identify vesicles per image by binary image analysis
% we apply pre-made ROIs for initial selection, one ROI is assumed to contain the life
% of one vesicle (the largest one in the box)

source=[init.exp_path,init.filename_green];
%image info:
first_im=imread(source,'Index',1);
[rr,cc]=size(first_im);
[XX,YY]=meshgrid(1:cc,1:rr);
info = imfinfo(source);    
[ff,~]=size(info); 

%pre-chosen Rois:
roidata=readtable([init.exp_path, init.filename_rois]);
pos_xx=roidata.X+roidata.Width/2;  %corner point plus half-width
pos_yy=roidata.Y+roidata.Height/2;  %analogous
pos_rr=roidata.Width/2; % app.radius
N_rois=length(pos_xx);
    
all_frames=struct('roi',[]);
for fri=1:ff+1-init.look_ahead
    disp(fri);
    %collect multiple images to suppress artefacts
    st=[];
    for sti=1:init.look_ahead
        st(:,:,sti)=((imread(source, fri+sti-1)));
    end
    im_ori=sum(st,3);

    for roi_i=1:N_rois
        im_buf=im_ori;
        xi=pos_xx(roi_i);
        yi=pos_yy(roi_i);
        roi_radius=pos_rr(roi_i);
        RR=((XX-xi).^2+(YY-yi).^2).^0.5;
        im_buf(RR>roi_radius)=0;       
        [props,label_im]=get_guvs(im_buf,'single');
        all_frames(fri).roi(roi_i).props=props;
        dum=1;
     end
    
    if fri==1
        example_im=label_im;
    end
    dum=1;
end
save([init.savepath, 'areadata.mat'], 'all_frames', 'example_im', 'first_im', 'roidata');

%get_guvs:
function [GUVs,labelmat]=get_guvs(im_ori, modus);
    minradius=25;
    minarea=pi*minradius.^2;
    minarea=250;
    im=matrix_blur_jk(double(im_ori),4);  %bit of smoothing
    [im_out,thr]=Find_treshold_MD_V2020(im,0); %tresholding
    BW1=uint16((im_out>0));
    BW2 = uint16(imfill(BW1, 'holes'));
    BW2 = uint16(bwmorph(BW2,'erode', 3));
    BW2 = uint16(bwmorph(BW2,'dilate', 3));
    
    %BW3 = uint16(bwmorph(BW2,'remove'));

    %% now, obtain shape data of the pore areas
    %run1;
    BW2_buf=BW2;
    bwstruct=bwconncomp(BW2,8);    %finds 8-fold connected regions.
    tempGUVs=regionprops(bwstruct, 'Area','PixelIdxList'); 
    for gi=1:length(tempGUVs)
        if tempGUVs(gi).Area<minarea
            pixelid=tempGUVs(gi).PixelIdxList;
            BW2_buf(pixelid)=0;
        end
    end
    %run 2
    BW2=BW2_buf;
    bwstruct=bwconncomp(BW2,8);    %finds 8-fold connected regions.
    GUVs=regionprops(bwstruct,...
        'Centroid', 'Area','MajorAxisLength',...
        'MinorAxisLength','Eccentricity','PixelIdxList','BoundingBox','Circularity'); 
    labelmat=labelmatrix(bwstruct); %label all the points in regions with the region nr
    
    if strcmp(modus, 'single')
        [GUVs, labelmat]=keep_largest(GUVs,labelmat);      
    end
    
    if 1
        figure;
        subplot(2,3,1); imshow(im_ori); title('original');
        subplot(2,3,2); imshow(im_out); title('smooth&treshold');
        subplot(2,3,3); imshow(double(BW1)); title('binary');
        subplot(2,3,4); imshow(double(BW2)); title('filled');
        subplot(2,3,5); pcolor(double(labelmat)); title('labeled'); shading flat, axis equal;
        pause(0.3);
        [~]=ginput(1);
    end

function [GUVs, labelmat]=keep_largest(GUVs,labelmat);
    areas=[]; 
    [N_guvs,~]=size(GUVs);
    for gi=1:N_guvs
        areas(gi)=GUVs(gi).Area;            
    end
    [~, largest_guv_idx]=max(areas);
    labelmat(labelmat~=largest_guv_idx)=0;
    labelmat(labelmat==largest_guv_idx)=1;
    bwstruct=bwconncomp(labelmat,8);    %finds 8-fold connected regions.
    GUVs=regionprops(bwstruct,...
    'Centroid', 'Area','MajorAxisLength',...
    'MinorAxisLength','Eccentricity','PixelIdxList','BoundingBox','Circularity'); 
    dum=1;