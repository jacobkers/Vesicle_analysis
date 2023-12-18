function A30_link_areas(init)
if 1
    load([init.savepath, 'areadata.mat'],'all_frames','example_im', 'first_im');    
    %first frame define first guvs with ID and startframe:
    %first detection counts. Then we fix the number
    [~,ff]=size(all_areas);
    [N_guvs,~]=size(all_areas(1).this_image);
    Guv_list=NaN*zeros(ff,N_guvs);
    Guv_list(1,:)=1:N_guvs;  
        %each column is a pointer to an area
        %one row is one frame
        %NaN means that no fitting area was found
 
    %Each GUV starts with its own ID in a row 1:N
    for fri=2:ff+1-init.look_ahead
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
                end
                %here, look for areas in former frame that overlap with this
                %one. if so, add the ID to former timeline. If not, add a new
                %one
            end
        end
    end
    dum=1;
end

save([init.savepath, 'areadata.mat'], 'Guv_list', '-append');

%A40_get_vesicle_lifes(init)
