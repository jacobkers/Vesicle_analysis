function [InnerSummary,RingSummary]=FF_Get_Object_Areas(FL0,fluotreshold);
%define 'edge' and 'inside' areas for later use
close all
[r,c]=size(FL0);
FL=JKD2_IM_smoothJK(FL0,5);

BW_pic=0*FL;
BW_pic(FL>fluotreshold)=1;

%clean up; aim is to get  clean closed areas  
    %modelpic=1.0*bwmorph(modelpic,'open');
    Ridge_w=15;
    BW_inner=BW_pic;
    for ii=1:2  %walk ring inward
        BW_edge = bwmorph(BW_inner,'remove');
        BW_edge = bwmorph(BW_edge,'dilate',Ridge_w);
        BW_inner=BW_inner&(~BW_edge);  %peel edge off
    end 
    if 0
        BW_edge_plot=1.0*BW_edge;
        BW_inner_plot=1.0*BW_inner;
        BW_edge_plot(BW_edge_plot==0)=NaN;
        BW_inner_plot(BW_inner_plot==0)=NaN;
        subplot(1,2,1); pcolor(BW_inner_plot.*FL0); colormap jet; shading flat;
        subplot(1,2,2); pcolor(BW_edge_plot.*FL0); colormap jet; shading flat;
    end    
[InnerObjects,InnerSummary]=Get_ObjectParameters(BW_inner,FL0);
[RingObjects,RingSummary]=Get_ObjectParameters(BW_edge,FL0);



function [objects,Summary]=Get_ObjectParameters(BW,FL0)
%%get object parameters and averages
objects = regionprops(BW, 'PixelIdxList', 'Area', 'EquivDiameter','Eccentricity','Centroid');
objects_I=regionprops(BW, FL0, 'MeanIntensity');
[ro,~]=size(objects);
LocalStds=zeros(ro,1);
LocalMeans=zeros(ro,1);
for ii=1:ro
    localvals=FL0(objects(ii).PixelIdxList);
    objects(ii).LocalStDev=std(localvals);
    objects(ii).LocalInt=objects_I(ii).MeanIntensity;
    LocalStds(ii)=objects(ii).LocalStDev;
    LocalMeans(ii)=objects_I(ii).MeanIntensity;
end
Summary.Count=ro;
Summary.AvLocalStd=mean(LocalStds);
Summary.AvLocalMean=mean(LocalMeans);
Summary.AvLocalRelStd=mean(LocalStds./LocalMeans);

dum=1;


