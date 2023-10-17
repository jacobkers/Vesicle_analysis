function guvalyzer

close all;

main_path='D:\jkerssemakers\CD_Data_in\2023_Rafael\';
%main_path='C:\Users\jkerssemakers\CD_Data_in\2023_Rafa\Test image analysis\';
exp_path=[main_path, '2023_10_02 Test image analysis\'];
%filename='40 uM LUVsWITHCerC6_RealTime_Series002_t000_overlay_green-1.tif';
filename='40 uM LUVsWITHCerC6_RealTime_Series002_t000_overlay.tif (red)-1.tif';
toolpath=swap_path('Dropbox\CD_recent\BN_CD22_Tisma\analysis\CD20_Cells\common_tools');
savepath=swap_path('Dropbox\CD_Data_out\2023_Rafael\2023_10_02 Test image analysis\');
addpath(genpath(toolpath));
source=[exp_path,filename];
first_im=imread(source,'Index',1);
[rr,cc]=size(first_im);
info = imfinfo(source);    
[ff,~]=size(info); 
look_ahead=5;

%% 1 A10_get areas
if 1    
    all_areas=struct('this_image',[]);
    for fri=1:ff+1-look_ahead
        disp(fri);
        st=[];
        for sti=1:look_ahead
            st(:,:,sti)=((imread(source, fri+sti-1)));
        end
        im_ori=sum(st,3);
        [props,label_im]=A001_get_guvs(im_ori);
        all_areas(fri).this_image=props;
        if fri==2
            example_im=label_im;
        end
        dum=1;
    end
    save([savepath, 'areadata.mat'],'all_areas', 'example_im');
end

%% 2) link areas
if 1
    load([savepath, 'areadata.mat'],'all_areas','example_im');
    
    %first frame define first guvs with ID and startframe:
    %first detection counts, we fix the number
    [N_guvs,~]=size(all_areas(1).this_image);
    Guv_list=NaN*zeros(ff,N_guvs);
    Guv_list(1,:)=1:N_guvs;  
        %each column is a pointer to an area
        %one row is one frame
        %NaN means that no fitting area was found
 
    %Each GUV starts with its own ID in a row 1:N
    for fri=2:ff+1-look_ahead
        [N_areas_this_frame,~]=size(all_areas(fri).this_image);
        last_list=Guv_list(fri-1,:);
        for guv_id=1:N_guvs
            guv_line=Guv_list(:,guv_id);
            sel=find(guv_line)
            guv_area_pointer=last_list(guv_id); %this points to the last associated areas
            if ~isnan(guv_area_pointer)  %if it was found last frame
                guv_props_lastframe=all_areas(fri-1).this_image(guv_area_pointer);
                former_pixels=guv_props_lastframe.PixelIdxList;
                %walk new areas in in the next 'lookahead' images
                area_candidates_overlap=[];
                area_candidates_area=[];
                
                for area_id=1:N_areas_this_frame
                    area_props_thisarea=all_areas(fri).this_image(area_id);
                    this_pixels=area_props_thisarea.PixelIdxList;
                    area_candidates_overlap(area_id)=any(ismember(this_pixels,former_pixels));
                    area_candidates_area_match(area_id)=abs(length(this_pixels)-length(former_pixels));
                end
                new_pointers=find(area_candidates_overlap==1);
                if ~isempty(new_pointers) %add to proper ID in last image
                    %new_pointer=new_pointer(1)
                    if length(new_pointers)>1
                        [~,bestfit]=min(area_candidates_area_match(new_pointers));
                        new_pointer=new_pointers(bestfit);
                    else
                        new_pointer=new_pointers;
                    end
                    Guv_list(fri,guv_id)=new_pointer;
                    %refine this: there can be multiple candidates (a 'split'); choose
                    %largest one of these to allocate in former frame and
                    %re-birth the rest 

                    dum=1;
                end
                %here, look for areas in former frame that overlap with this
                %one. if so, add the ID to former timeline. If not, add a new
                %one
            end
        end
    end
    dum=1;
end

figure;
subplot(2,3,1); pcolor(first_im); shading flat, colormap jet; axis equal; axis tight
title('first frame');
subplot(2,3,4); pcolor(example_im); shading flat, colormap jet; axis equal; axis tight
title('detected');
subplot(1,3,2);
for guv_id=1:N_guvs
    %build any property
    frame_line=[];
    property1=[];
    property2=[];
    for fri=1:ff
        guv_pointer=Guv_list(fri,guv_id);
        if ~isnan(guv_pointer)
            frame_line(fri)=fri;
            property1(fri)=all_areas(fri).this_image(guv_pointer).Area;
            property2(fri)=all_areas(fri).this_image(guv_pointer).Circularity;
        end
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

%get_guvs:
function [GUVs,labelmat]=A001_get_guvs(im_ori);
    minradius=25;
    minarea=pi*minradius.^2;
    minarea=250;

    im=matrix_blur_jk(double(im_ori),4);  %bit of smoothing
    [im_out,thr]=Find_treshold_MD_V2020(im,0); %tresholding
    BW1=uint16((im_out>0));
    BW2 = uint16(imfill(BW1, 'holes'));
    BW2 = bwmorph(BW2,'erode', 3);
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
