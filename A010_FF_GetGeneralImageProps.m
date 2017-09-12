function A010_FF_GetGeneralImageProps(batchrunindex)
% 'Use this section for a Quicksheet'
%------------------------------------------------------------
    %This function performs batch analysis on images. 
    % Jacob Kerssemakers 2017 
%------------------------------------------------------------[JK16]
% 'End of Quicksheet section'

close all;

initval=A000__WF_Get_FF_PathsandExperiments(batchrunindex);
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
    ImagePropertyList=zeros(LP,9);
    for jj=1:LP
        %load the image
        disp(strcat(SaveName,'_',num2str(LP-jj+1), 'images to go'));       
        dirname=image_list(jj).dirname;
        filname=image_list(jj).filname;
        LabelList=[LabelList; {filname(1:end-4)}];       
        im=double(imread(strcat(dirname,initval.DirSep,filname)));
        
        %fluorescence analysis
        [fluo,modelpic]=FF_Basic_Fluorescence(im,3);
        [InnerSummary,RingSummary]=FF_Get_Object_Areas(im,fluo.level_fluotreshold);             
        ImagePropertyList(jj,:)=[jj, ...         
        InnerSummary.Count,...
        InnerSummary.AvLocalStd,...
        InnerSummary.AvLocalMean,...
        InnerSummary.AvLocalRelStd,...
        RingSummary.Count,...
        RingSummary.AvLocalStd,...
        RingSummary.AvLocalMean,...
        RingSummary.AvLocalRelStd];
        
        if 0
        %if jj==1|jj==LP
            pcolor(modelpic.*im); shading flat; axis equal; colormap jet;
            title(strcat(SaveName,'Image',num2str(jj)));
            fluo
            pause(0.1);
            [~]=ginput(1);
        end
        %LabelList
    end 
    %plot the result
    close all;
    set(figure(2), 'visible','off')
    plot(ImagePropertyList(:,1),ImagePropertyList(:,5),'o-', 'LineWidth',2); hold on;
    plot(ImagePropertyList(:,1),ImagePropertyList(:,9),'ro-', 'LineWidth',2);
    title('standard deviation vs. time, droplet average');
    xlabel('frame time');
    ylabel('std/mean, [-]');
    legend('inside areas', 'edges');
    saveas(gcf,strcat(initval.resultpath,SaveName,'_A010_ImageProperties'),'jpg');  
    
    
    
    %% save the result to a properly named output
    ColNames=Build_Headers;   
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),ColNames,'Sheet1','A1');
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),LabelList,'Sheet1','A2');
     xlswrite(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.xlsx'),ImagePropertyList,'Sheet1','B2');
     save(strcat(initval.resultpath,SaveName,'_A010_ImageProperties.mat'),'ImagePropertyList');             
    dum=1;
end

 function ColNames=Build_Headers;
     ColNames=[{'filename'}, {'index'},...
        {'InsideObjectCount'},...
        {'InsideAvLocalStd'},...
        {'InsideAvLocalMean'},...
        {'InsideAvLocalRelStd'},...
        {'RingObjectCount'},...
        {'RingAvLocalStd'},...
        {'RingAvLocalMean'},...
        {'RingAvLocalRelStd'}];

function SaveName=Build_SaveName(initval,dirnm,DataType);
    %build a save name
    lsourcename=length(initval.datasourcepath);
    subdirnm=dirnm(lsourcename+1:end);
    ix=strfind(subdirnm, initval.DirSep);
    if ~isempty(ix)
        subdirnm(ix)='_';
    end
    SaveName=strcat(initval.expi,'_',DataType,'_',subdirnm);


