function  pretracksettings=TrackXY_by_QI_Init(firstim)
%JWJK:This function intializes settings for a sub-pixel XY fit by making 4 profiles in QI
%style. Algorithm described in 
%[1]: M.T.J. van Loenhout, J. Kerssemakers , I. De Vlaminck, C. Dekker
% Non-bias-limited tracking of spherical particles, enabling nanometer 
%resolution at low magnification
% Biophys. J. 102, Issue 10, 2362 (2012)

%Set includes following functions:
% TrackXY_by_QI: main
% TrackXY_by_QI_Init: initialization via first image 
% TrackXY_by_COM_2Dmoment: first gues center-of mass
% SymCenter: sub-pixel 1D fit
% MakeHighResRing: genarates artificial image for demo purposes

%Jacob Kerssemakers, 2017
%:JWJK--------------------------------------------

%general settings, see ref [1] for details
    pretracksettings.radialoversampling=2;  
        %default 2 (per image pixel length)
    pretracksettings.angularoversampling=0.7; 
        %deault 0.7 typically covers all image pixels
    pretracksettings.minradius=0; 
    pretracksettings.maxradius=min(size(firstim))/2;
    pretracksettings.iterations=10; 
        %number of times refinement of center is repeated; typically minimal 5        
    pretracksettings=Build_QI_SamplinggridGrid(pretracksettings) ;
        %relative coordinates of radial sampling grid; calculatedbeforehand
        %to save time
            
function QI=Build_QI_SamplinggridGrid(QI) 
    %Build a radial sampling grid; based on image size
    spokesnoperquad=ceil(2*pi*QI.maxradius*QI.angularoversampling/4);
    radbinsno=(QI.maxradius-QI.minradius)*QI.radialoversampling;
    angles=linspace(-pi/4,2*pi-pi/4,spokesnoperquad*4+1)'; 
    angularstep=pi/2/spokesnoperquad;
    angles=angles(1:end-1)+angularstep/2; %to center angles per quadrant
    radbins=linspace(QI.minradius,QI.maxradius,radbinsno);
    [argsgrid,radiigrid]=meshgrid(angles,radbins);
    QI.Y0samplinggrid=(radiigrid.*sin(argsgrid))';
    QI.X0samplinggrid=(radiigrid.*cos(argsgrid))';
    QI.angles=angles;
    QI.radbii=radbins;
    