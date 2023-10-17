function A20_get_areas(init);
% identify vesicles

source=[init.exp_path,init.filename];
first_im=imread(source,'Index',1);
[rr,cc]=size(first_im);
info = imfinfo(source);    
[ff,~]=size(info); 

if 1    
    all_areas=struct('this_image',[]);
    for fri=1:ff+1-init.look_ahead
        disp(fri);
        st=[];
        for sti=1:init.look_ahead
            st(:,:,sti)=((imread(source, fri+sti-1)));
        end
        im_ori=sum(st,3);
        [props,label_im]=get_guvs(im_ori);
        all_areas(fri).this_image=props;
        if fri==1
            example_im=label_im;
        end
        dum=1;
    end
    save([init.savepath, 'areadata.mat'],'all_areas', 'example_im', 'first_im');
end

%get_guvs:
function [GUVs,labelmat]=get_guvs(im_ori);
    minradius=25;
    minarea=pi*minradius.^2;
    minarea=250;
    im=matrix_blur_jk(double(im_ori),3);  %bit of smoothing
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
    
    if 0
        figure;
        subplot(2,3,1); imshow(im_ori); title('original');
        subplot(2,3,2); imshow(im_out); title('smooth&treshold');
        subplot(2,3,3); imshow(double(BW1)); title('binary');
        subplot(2,3,4); imshow(double(BW2)); title('filled');
        subplot(2,3,5); pcolor(double(labelmat)); title('labeled'); shading flat, axis equal;
        pause(0.3);
        %[~]=ginput(1);
    end

