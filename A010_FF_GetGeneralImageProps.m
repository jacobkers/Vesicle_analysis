function A010_FF_GetGeneralImageProps(batchrunindex)
% 'Use this section for a Quicksheet'
%------------------------------------------------------------
    %This function performs batch analysis on images. 
    % Jacob Kerssemakers 2017 
%------------------------------------------------------------[JK16]
% 'End of Quicksheet section'

close all;

initval=A000__WF_Get_FF_PathsandExperiments(batchrunindex);;
 if isdir(initval.resultpath), rmdir(initval.resultpath,'s');  end
    mkdir(initval.resultpath);
    %mkdir(strcat(initval.resultpath,'CellImages_All',initval.DirSep));

    
    %collect direcories that contain tif images
[~, filled_dir_list]=Scroll_ImageDirs(initval.datasourcepath,'*.tif');
LD=length(filled_dir_list);
%work through the directories
for ii=1:LD
    dirnm=filled_dir_list(ii).dirname;
    LabelList=cell(0);
    %check if stack or timelapse; build savename
    DataType='Unknown';
    if strfind(dirnm, 'stack'), DataType='Stack';end
    if strfind(dirnm, 'mins');  DataType='TimeLapse';end
    SaveName=Build_SaveName(initval,dirnm,DataType);
    %work images
    [image_list,~]=Scroll_ImageDirs(dirnm,'*.tif');
    LP=length(image_list);
    ImagePropertyList=zeros(LP,3);
    for jj=1:LP
        %load the image
        disp(strcat(SaveName,'_',num2str(LP-jj+1), 'images to go'));       
        dirname=image_list(jj).dirname;
        filname=image_list(jj).filname;
        LabelList=[LabelList; {filname(1:end-4)}];
        im=double(imread(strcat(dirname,initval.DirSep,filname)));
        std_im=std(im(:));
        mn_im=mean(im(:));
        ImagePropertyList(jj,:)=[jj mn_im std_im];
        %do the analysis
        if 0
            pcolor(im); shading flat; axis equal; colormap bone;
            title(strcat(SaveName,'Image',num2str(jj)));
            pause(0.1); 
        end
        %LabelList
    end    
    %% save the result to a properly named output
   
    
    
    %post-processing         
     ColNames=[{'filename'}, {'index'},{'image mean'}, {'image std'}];
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),ColNames,'Sheet1','A1');
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),LabelList,'Sheet1','A2');
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),ImagePropertyList,'Sheet1','B2');
     %xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A010_ImageProperties.xlsx'),LabelList ,'Sheet1','A2');
     %xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A010_ImageProperties.xlsx'),AllCellBasicGeometries ,'Sheet1','A2');
    %     save(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A010_ImageProperties.mat'),'AllCellBasicGeometries');             
    dum=1;
end




function SaveName=Build_SaveName(initval,dirnm,DataType);
    %build a save name
    lsourcename=length(initval.datasourcepath);
    subdirnm=dirnm(lsourcename+1:end);
    ix=strfind(subdirnm, initval.DirSep);
    if ~isempty(ix)
        subdirnm(ix)='_';
    end
    SaveName=strcat(initval.expi,'_',DataType,'_',subdirnm);


