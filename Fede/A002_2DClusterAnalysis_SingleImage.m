function A002_2DClusterAnalysis_SingleImage
%JWJK_A:-------------------------------------------------------------------
%Two-dimensional (image-based) cluster analysis
%
%Summary: This function performs 2D cluster analysis on chromatin patterns of 
%cells and stores the result per cell, per cluster.
%
%Approach: we deconstruct the image by means of single-spot, psf-sized
%Gaussians. This is done by subtracting such Gaussians from the image by
%fist picking the brightest image point and subtracting one Gaussian of
%equal peak intensity there, then repeating this action on the residual
%image and continuing to do so until all intensity is covered by the subtracted 
%Gaussians.
%Next, the Gaussians are grouped in clusters. Each cluster consists of a
%small group of Gaussians(typically 1-5) or 'components' that are within one psf 
%distance of one of the others, such that the cluster forms an optically connected shape. 
%Likewise, all components of one cluster are at least one psf away form
%those of another.
%These clusters are then parametrized by their center-of mass position,
%content, radius of gyration and so on. Finally, their angular position with respect to  
% the chromatin geometrical center (as was determined via the 1D density curve analysis)
% is determined and stored.
%
%Input: data in .mat files stored in former analysis steps.
%
%Output: Data is presented as scatter plots and histograms. Saved are 
%Tabular excel files, .mat and summary plots.
%
%:JWJK_A-------------------------------------------------------------------
close all;

Psf_meas=20;
allframes=length(initval.Cell_Labels);


imoutdir=strcat(initval.resultpath,'CellImages_Clusteranalysis',initval.DirSep);  
if isdir(imoutdir), 
    rmdir(imoutdir,'s');  end
mkdir(imoutdir);
MatFileDir=strcat(initval.resultpath,'ResultsPerCellMatlab',initval.DirSep); 
% if isdir(MatFileDir), 
%     rmdir(MatFileDir,'s');  end
% mkdir(MatFileDir);

AllCellsAllClusters=[];
AllClusters=[];
ClusterMaxNo=0;




%im=proper cut from stack
for jj=1:allframes           
    AllSpotProps=PeelblobsFromImage(im,Psf_meas,0.98,0.03, 0); 
    AllSpotProps=F006_CleanSpots(AllSpotProps,im,Psf_meas);      
    [rr,~]=size(AllSpotProps);        
    if rr>1
        x=AllSpotProps(:,3);        y=AllSpotProps(:,4);
        ClusterBasics=Find_Clusters(AllSpotProps, initval);
        %Build single cluster contours
        [Clusters,ClusterPropsRow,ThisCellClusterTable,AllContoursX,AllContoursY,ReconstructIm]=GetClusterDetails(ClusterBasics,im);
        [~,clusterno]=size(Clusters);
        ClusterMaxNo=max([ClusterMaxNo clusterno]); %needed for table header

        %add to full per-cell-table, elongate if necessary
        [rr,cc]=size(AllCellsAllClusters);
        newrowentry=[CellSpecs clusterno ClusterPropsRow]; le=length(newrowentry);
        cc_new=max([cc,le]);        
        newtable=zeros(rr+1,cc_new); 
        newtable(1:rr,1:cc)=AllCellsAllClusters;
        newtable(rr+1,1:le)=newrowentry;
        AllCellsAllClusters=newtable;

        %add to cluster-sorted table
        AllClusters=[AllClusters; ...
                    [repmat(CellSpecs,clusterno,1)...
                     ThisCellClusterTable]];
        save(strcat(MatFileDir,CellName,'_Clusters.mat'),'Clusters','chro_pic');                                                                    

   %% PLOT MENU---------------------------------------------------------------
    if initval.showplots
        set(figure(1), 'visible','on')
    else
        set(figure(1), 'visible','off')
    end

%% plot the cromosome pattern
%things we plot per cell
plot_pic=-im+max(im(:));    

PlotProps=AllSpotProps;   
perc=num2str(round(100*PlotProps(end,7)));
title(strcat('Overlay covering',perc,'percent'));
scale=24/max(PlotProps(:,6));

    if 1 %things we do plot
        pcolor(plot_pic'); shading flat, colormap bone; hold on;
        pause(0.1);
        %V3: add contour lines of original
        contour(im',6,'k','Linewidth',1); hold on;
        axis equal; axis tight; axis xy; hold on; 
         %V1: add contour lines of clusters

        saveas(gcf,strcat(imoutdir,'CellClusters', num2str(cellno,'% 3.0f'),'.jpg')); 
        %pause(0.3); 
        %close(gcf);
    else  %things one could plot (but we don't)
        %% plot per cluster
        [~,CL]=size(Clusters);
        clrs=['ro-';'bo-';'mo-';'go-'; 'yo-'; 'co-'];
        for cc=1:CL
        %plot(Clusters(cc).COM_Y,Clusters(cc).COM_X,'r*', 'MarkerSize',5); hold on; 
        %text(Clusters(cc).COM_Y,Clusters(cc).COM_X,strcat('--',num2str(Clusters(cc).COM_DistPerc))),
        hold on;
        clri=mod(cc,5)+1; 
        clr=clrs(clri,:); 
        clr='ro-';
        clus_x=Clusters(cc).spotprops(:,3);
        clus_y=Clusters(cc).spotprops(:,4); 
        mrksize=ceil(Clusters(cc).spotprops(:,6)*scale);
        lc=length(clus_x);
        plot(clus_y,clus_x,clr,'MarkerSize',1,'LineWidth',2); hold on;   
        for lci=1:lc  %per-cluster gaussian components
            plot(clus_y(lci),clus_x(lci),clr,'MarkerSize',...
            max([mrksize(lci) 1]),'LineWidth',2); hold on;
        end

        end
        pcolor(chro_pic); colormap bone; shading flat; hold on;
        pause(0.01);
        saveas(gcf,strcat(imoutdir,'CellClusters', num2str(cellno,'% 3.0f'),'.jpg')); 
        pause(0.01); 
        if sho
            [~]=ginput(1); 
        end
    end
    end
    %% end of cluster analysis section
end


%% wrapping up for saving: cluster report
    [rr,cc]=size(AllCellsAllClusters);
    CellProps_Av=zeros(1,cc);
    CellProps_Std=zeros(1,cc);
    for ii=1:cc
        bufcol=AllCellsAllClusters(:,ii); bufcol=bufcol(bufcol>0);
        CellProps_Av(ii)=nanmean(bufcol);
        CellProps_Std(ii)=nanstd(bufcol);
    end
    CellProps_Av(1:2)=[-1 -10000];
    CellProps_Std(1:2)=[-2 -10000];

    AllCellsAllClusters=[CellProps_Av;
                    CellProps_Std;
                    AllCellsAllClusters];

    [Header,Headershort]=Build_cluster_Excel_Header(ClusterMaxNo);

    [rr,cc]=size(AllCellsAllClusters);
    erasersheet=NaN*zeros(2E3,2*cc);
    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_Cell_ClusterReport.xlsx'),Header,'Sheet1','A1');
    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_Cell_ClusterReport.xlsx'),erasersheet,'Sheet1','A3');
    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_Cell_ClusterReport.xlsx'),AllCellsAllClusters,'Sheet1','A3');
    save(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_Cell_ClusterReport.mat'),'AllCellsAllClusters');


    [rr2,cc2]=size(AllClusters);
    erasersheet2=NaN*zeros(10E4,2*cc2);

    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_ClusterColumnReport.xlsx'),Headershort,'Sheet1','A1');
    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_ClusterColumnReport.xlsx'),erasersheet2,'Sheet1','A2');
    xlswrite(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_ClusterColumnReport.xlsx'),AllClusters,'Sheet1','A2');
    save(strcat(initval.resultpath,initval.DirSep,initval.expi,'_A050_ClusterColumnReport.mat'),'AllClusters');

        if 0
        % wrapping up for saving: cluster position curves
        ClusterWeightedPosAxis;
        ClusterWeightedPosCurves_DS_av=(nanmean(ClusterWeightedPosCurves_DS'))';
        ClusterWeightedPosCurves_BP_av=(nanmean(ClusterWeightedPosCurves_BP'))';
        ClusterWeightedPosCurves_DS;
        ClusterWeightedPosCurves_BP;
        end



function Clusters=Find_Clusters(SpotProps, initval);
% 'Use this section for a Quicksheet'
%------------------------------------------------------------
    % sort spots by brightness; pick brightest one
    % find near ones for brightmost one from leftover list
    % for the ones found, keep finding new near ones until nochange; 
   
        % repeat for leftovers until no leftovers
        %JacobKers 2017 ----------------------------------------
        %AllSpotProps=[
        % 1 spotcount 
        % 2 Peak 
        % 3 Xpos 
        % 4 Ypos 
        % 5 Psf 
        %6 ThisSpotFraction 
        %7CoveredFraction 
        %8 RelChange]];
%------------------------------------------------------------[JK16]
% 'End of Quicksheet section'

 left_ones=SpotProps;
 Clusters=struct([]);
 N_clust=0;
 ClusterTable=[];
 while ~isempty(left_ones);    
    %build a new cluster
    N_clust=N_clust+1;
    Bri=left_ones(:,6); 
    thiscluster=left_ones(1,:);
    left_ones=left_ones(2:end,:);  %pick from stock
    [LC,~]=size(thiscluster);
    cluster_growth=1;
    while cluster_growth
        new_ones=[];
        for ii=1:LC  
            %for all existing elements of this cluster, 
            %,find near ones in the leftover stock
            x0=thiscluster(ii,3);
            y0=thiscluster(ii,4);
            leftx=left_ones(:,3);
            lefty=left_ones(:,4);
            rr=((leftx-x0).^2+(lefty-y0).^2).^0.5;
            SeparateWidth=2.5;
            near_ones_idx=find(rr<SeparateWidth*initval.Psf_est); %overlapping
            left_ones_idx=find(rr>=SeparateWidth*initval.Psf_est); 
          
            if ~isempty(left_ones_idx)
                new_ones=[new_ones; left_ones(near_ones_idx,:)]; %add 
                left_ones=left_ones(left_ones_idx,:);  %shrink remaining                 
            end
        end
        if ~isempty(new_ones) 
            thiscluster=[thiscluster; new_ones]; %add new ones to cluster 
        else
            cluster_growth=0;  %...or stop this cluster
        end 
    end
    %add values to cluster struct; go to next
    Clusters(N_clust).spotprops=thiscluster;    
 end


function [Clusters,ThisCellClusterRow,ThisCellClusterTable,AllContoursX,AllContoursY,ReconstructIm]=GetClusterDetails(Clusters,orim)
% 'Use this section for a Quicksheet'
%------------------------------------------------------------
    % this function works trhough all clusters in a cell:
    % builds a single-cluster image and obtains properties for this.
     %input: AllSpotProps, collection of contributing Gaussian spots
        % 1 spotcount 
        % 2 Peak 
        % 3 Xpos 
        % 4 Ypos 
        % 5 Psf 
        %6 ThisSpotFraction 
        %7CoveredFraction 
        %8 RelChange]];
    % It also builds a clustercontour(level) using the FWHM lelvel 
    % points (or other levels)
        %Clusters
        %Contours
        %ThisCellClusterTable contains sorted  'CL' rows of:
        %order content% area radius density xpos ypos 1Ddistpos 1DBPpos
%------------------------------------------------------------[JK16]
% 'End of Quicksheet section'
 
    [rr,cc]=size(orim);
    [XX,YY]=meshgrid(1:cc,1:rr);    
    [~,CL]=size(Clusters);
    AllContoursX=zeros(50,CL);
    AllContoursY=zeros(50,CL);
    ThisCellClusterTable=zeros(CL,9);
    %contains 'CL' rows of:
    %order content% area radius density xpos ypos 1Ddistpos 1DBPpos
    ReconstructIm=0*orim;   
     for ii=1:CL  %FOR ALL CLUSTERS
             
        ThisClusterSpots=Clusters(ii).spotprops;  %components of cluster
        thisclusterim=GetSingleClusterImage(ThisClusterSpots,orim); 
        ReconstructIm=ReconstructIm+thisclusterim;
        C_perc=sum(ThisClusterSpots(:,6));
        psf_used=ThisClusterSpots(1,5);
        
        %cluster parameters
        %[x_com,y_com,~,~]=TrackXY_by_COM_2Dmoment(thisclusterim);
        
        
        [x_com,y_com,~,~,rad_gyr]=JKD2_IM_calculate2Dmoment_extended(thisclusterim);
        if 0 %strcmp(cellno,'200020')
            pcolor(thisclusterim'); shading flat, colormap bone;
            title(['Cluster' num2str(ii)]);
             axis equal; axis tight; axis xy; hold on;
            [~]=ginput(1);
        end                               
        [contourX,contourY,ClusterShapeProps,clustermask]=GetClusterShapeProps(thisclusterim,orim,x_com,y_com,0.2); 
        
        AllContoursX(:,ii)=contourX;
        AllContoursY(:,ii)=contourY;
        
        %add properties to clustertable
        thisclusterprops=[C_perc.... 
                          2*rad_gyr ...                         
                          ClusterShapeProps.EquivDiameter...
                          2*ClusterShapeProps.RgBW... 
                          ClusterShapeProps.Area... 
                          ClusterShapeProps.Density ...
                          x_com... 
                          y_com...  
                          psf_used...
                          ];
            %order content% area radius density xpos ypos 1Ddistpos 1DBPpos
        ThisCellClusterTable(ii,:)=thisclusterprops;
      
        %add properties to 'Cluster' structure
        Clusters(ii).COM_X=x_com;  %[x,y];
        Clusters(ii).COM_Y=y_com;  %[x,y]; 
        Clusters(ii).C_perc=C_perc;                       
        Clusters(ii).EquivDiameter=ClusterShapeProps.EquivDiameter;
        Clusters(ii).Area=ClusterShapeProps.Area; 
        Clusters(ii).Density=ClusterShapeProps.Density;
        Clusters(ii).psf_used=psf_used; 
        Clusters(ii).clustermask=clustermask;
     end
     
     %Sort cluster table by brightest cluster first, transform  to one row
     %content% radius area density xpos ypos 1Ddistpos 1DBPpos
     [rr,cc]=size(ThisCellClusterTable);
     [~,idx]=sort(ThisCellClusterTable(:,1),'descend');
     ThisCellClusterTable=ThisCellClusterTable(idx,:);
     ThisCellClusterRow=reshape(ThisCellClusterTable',1,rr*cc); %repeat=8;
      
  function [contourX,contourY,ClusterShapeProps,BW]=GetClusterShapeProps(thisclusterim,orim,xm,ym,cutoff);
      %This function obtains contour points of an spheroid contour, equally
      %spaced, in order of angular revolution around the COM and with a
      %fixed number of points
                BW=0*thisclusterim;
                [rr,cc]=size(thisclusterim);
                [XX,YY]=meshgrid(1:cc,1:rr);
                sel=find(thisclusterim>cutoff*max(orim(:)));
                if length(sel)>1
                BW(sel)=1;   
                ClusterShapeProps = regionprops(BW, 'Area','EquivDiameter');
                ClusterShapeProps.Density=sum(thisclusterim(sel))/length(sel);
                
                [xBW,yBW,~,~,RgBW]=JKD2_IM_calculate2Dmoment_extended(1.0*BW);
                ClusterShapeProps.xBW=xBW; 
                ClusterShapeProps.yBW=yBW; 
                ClusterShapeProps.RgBW=RgBW; 
                
                BWedge=bwmorph(BW,'remove');
                contourX=XX(BWedge);
                contourY=YY(BWedge);
                
                angle=atan2(contourY-ym,contourX-xm);
                [~,idx]=sort(angle);
                contourX=contourX(idx);
                contourY=contourY(idx);
                [contourX,contourY]=B002_EqualizeAlongContour(contourX,contourY,49); 
                %close contour lines by repeating start point at end
                contourX=[contourX ;contourX(1)];
                contourY=[contourY ;contourY(1)];
                
                else
                    contourX=NaN*ones(50,1);
                    contourY=NaN*ones(50,1);      
                    ClusterShapeProps.Area=NaN;
                    ClusterShapeProps.EquivDiameter=NaN;
                    ClusterShapeProps.Density=NaN;
                    ClusterShapeProps.xBW=NaN; 
                    ClusterShapeProps.yBW=NaN; 
                    ClusterShapeProps.RgBW=NaN; 
                end
                
 function thisclusterim=GetSingleClusterImage(ThisClusterSpots,orim);
        %1) build a one-cluster-image
        thisclusterim=0*orim;
         [Nspots,~]=size(ThisClusterSpots);
        for jj=1:Nspots
            Xpos=ThisClusterSpots(jj,3);
            Ypos=ThisClusterSpots(jj,4);
            Psf=ThisClusterSpots(jj,5);
            Peak=ThisClusterSpots(jj,2);
            thisclusterim=thisclusterim+Peak*TwoDGaussNormPeak(orim,Xpos,Ypos,Psf);   
        end
        
        
function [Header,Headershort]=Build_cluster_Excel_Header(ClusterMaxNo);
     %this function builds headers for the table
       %Labels (case and space sensitive!):
   General = [{'index'} ,...
           {'label'}, ....
           {'cluster number'}];     
   ParamsNames =[...      
        {'content'},...     %1
        {'diameter_2Rg'},...     %2
        {'diameter_ContourBW_Equiv'},...     %2
        {'diameter_ContourBW_2Rg'},...     %2        
        {'area'},...  %3
        {'density'},...  %4
        {'xpos'},...  %5
        {'ypos'},...  %6
        {'1Ddistpos'},...  %7
        {'1DBPpos'},...  %8
        {'Psf_used'},...  %8
        ];
        
        HeaderRow1=cell(0,0); 
        HeaderRow2=cell(0,0);
        
        %1) build first part-----------------------------------------------
        GE=length(General);
        for sl=1:GE
            HeaderRow1=[HeaderRow1 {'General parameters'}];    
        end
        HeaderRow2=General;
      
        %2) build second part-----------------------------------------------
        LP=length(ParamsNames);
        for ss=1:ClusterMaxNo
            ClusterName=strcat('Cluster',num2str(ss,'%02.0f'));
            for pp=1:LP
                HeaderRow1=[HeaderRow1 cellstr(ClusterName)];
                HeaderRow2=[HeaderRow2 ParamsNames{pp}];
            end
        end
       Header=[HeaderRow1; HeaderRow2];     
      Headershort=[General(1:2) ParamsNames]; 
        
    
      
        
        
        
        
        