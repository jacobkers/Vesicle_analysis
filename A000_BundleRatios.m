
function A000_BundleRatios
addpath(genpath('C:\Users\jkerssemakers\Dropbox\CD_recent\BN_CD16_Fede\FedeMatlabCode\'));
close all;
for expi=1:1  
    %1: no bundles 
    %2: bundles, not bleached
        
    %0: bundles, bleached 
    %1: no bundles 
    %2: bundles, not bleached
    %3: time evolution (run only Get_radialmaps_t)
    close all;
    initval=Set_Data(expi,1);  %just to get general info
    LD=length(initval.droplet.allno);   
    
    for dr=1:LD
        disp(strcat('Exp..', num2str(expi),'droplet', num2str(dr)));  

        initval=Set_Data(expi,dr);  %expi, droplet
        
        %things we can do
        if 0, Plot_ratio_per_pixel(initval); end
        if 0, Get_selected_Z_profiles(initval,dr); end
        if 1, 
            if dr==1, profileresults=[];; end
            profileresults=Get_equator_crosslines(initval,dr,profileresults); end
        if 0, 
            if dr==1, bleachinfo=Init_Results; end
            bleachinfo=Get_radialmaps_t(initval,dr,bleachinfo); end
                        %build this against time, per droplet
    end    
end

%% wrappingup and saving
if (expi==1)||(expi==2)
  save([initval.savedir,initval.savename,'_SUMMARY.mat'],'profileresults');
end
if expi==3;
    bleachinfo.mean_tau_f_pk=round(nanmean(bleachinfo.decay_f_pk));
    bleachinfo.mean_tau_z_pk=round(nanmean(bleachinfo.decay_z_pk));
    bleachinfo.median_tau_f_pk=round(nanmedian(bleachinfo.decay_f_pk));
    bleachinfo.median_tau_z_pk=round(nanmedian(bleachinfo.decay_z_pk));
    bleachinfo.std_tau_f_pk=round(std(bleachinfo.decay_f_pk));
    bleachinfo.std_tau_z_pk=round(std(bleachinfo.decay_z_pk));

    bleachinfo.mean_tau_f_plat=round(nanmean(bleachinfo.decay_f_plat));
    bleachinfo.mean_tau_z_plat=round(nanmean(bleachinfo.decay_z_plat));
    bleachinfo.median_tau_f_plat=round(nanmedian(bleachinfo.decay_f_plat));
    bleachinfo.median_tau_z_plat=round(nanmedian(bleachinfo.decay_z_plat));
    bleachinfo.std_tau_f_plat=round(std(bleachinfo.decay_f_plat));
    bleachinfo.std_tau_z_plat=round(std(bleachinfo.decay_z_plat));

    [bleachinfo.decay_f_pk' ...
     bleachinfo.decay_f_plat' ...
     bleachinfo.decay_z_pk' ...
     bleachinfo.decay_z_plat' ...
     ]
     save([initval.savedir,initval.savename,'_summaryresults.mat'],'initval','bleachinfo');
end

function Get_selected_Z_profiles(initval,dr);
%eq=initval.bot_eq_top_planes(2);
[imlist_f,~]=Scroll_ImageDirs(initval.dir_FtsZ  ,'*.tif');
[imlist_z,~]=Scroll_ImageDirs(initval.dir_ZipA  ,'*.tif');

FF=length(imlist_f);
eq=initval.droplet.eq(dr);
im_eq=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(eq).filname))),initval.smoothim);
[rr,cc]=size(im_eq);

x0=ceil(cc/2);
y0=ceil(rr/2);

areasel_c=get_areasel(x0,y0,rr,cc,10);
im_eq(areasel_c)=NaN;

areasel_b=get_areasel(1,1,rr,cc,20);
im_eq(areasel_b)=NaN;

subplot(1,2,1);
pcolor(im_eq); colormap bone, shading flat; axis equal, axis tight;
pause(0.1);

for fr=1:FF
    im_f=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(fr).filname))),initval.smoothim);
    im_z=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_ZipA,imlist_z(fr).filname))),initval.smoothim);
    %im_f=im_f-min(im_f(:));
    %im_z=im_z-min(im_z(:));
    counts_f(fr)=mean(im_f(areasel_c));
    counts_z(fr)=mean(im_z(areasel_c));  
    counts_fb(fr)=mean(im_f(areasel_b));
    counts_zb(fr)=mean(im_z(areasel_b));  
end
subplot(1,2,2); 
    plot(counts_f,'b'); hold on;
    plot(counts_z,'r'); hold on;
    plot(counts_fb,'b'); hold on;
    plot(counts_zb,'r'); hold on;
    legend('FtzZ','ZipA','FtzZ-background','ZipA-background');
    xlabel('plane')
    ylabel('counts')
    
function areasel=get_areasel(x0,y0,rr,cc,radius)
[XX,YY]=meshgrid(1:cc,1:rr);
RR=((XX-x0).^2+(YY-y0).^2).^0.5;
areasel=find(RR<radius);    


function profileresults=Get_equator_crosslines(initval,dr,profileresults);
    
    [im_eq_f,im_eq_z]=Fetch_imagepair(initval,dr);    
    
    [radialprofile_f,radialmap_f]=Build_radial_profile(im_eq_f,initval,dr);
    [radialprofile_z,radialmap_z]=Build_radial_profile(im_eq_z,initval,dr);
    
    profileprops_f=Get_profile_properties(radialprofile_f);
    profileprops_z=Get_profile_properties(radialprofile_z); 
    
    if 0
    profileresults=[profileresults; round([dr profileprops_f.pk_pos   profileprops_f.pk_val  profileprops_f.plat_val ...
        profileprops_z.pk_pos   profileprops_z.pk_val  profileprops_z.plat_val])]
    else
        profileresults.dropno(dr,:)=dr;
        profileresults.FtsZ_pos(dr,:)=profileprops_f.pk_pos;
        profileresults.FtsZ_pkval(dr,:)=profileprops_f.pk_val;
        profileresults.FtsZ_platval(dr,:)=profileprops_f.plat_val;
        profileresults.ZipA_pos(dr,:)=profileprops_z.pk_pos;
        profileresults.ZipA_pkval(dr,:)=profileprops_z.pk_val;
        profileresults.ZipA_platval(dr,:)=profileprops_z.plat_val;
        profileresults.FZ_Ratio_plat(dr,:)=profileprops_f.plat_val/profileprops_z.plat_val;
        profileresults.FZ_Ratio_peak(dr,:)=profileprops_f.pk_val/profileprops_z.pk_val;
    end
    
   
    if 1, Plot_Save_stuff_A000_line116(im_eq_f,im_eq_z,radialmap_f,radialmap_z,radialprofile_f',radialprofile_z',initval); end

function bleachinfo=Get_radialmaps_t(initval,dr, bleachinfo)
    [imlist_f,~]=Scroll_ImageDirs(initval.dir_FtsZ  ,'*.tif');
    [imlist_z,~]=Scroll_ImageDirs(initval.dir_ZipA  ,'*.tif');
    image_idxlist=initval.droplet.zplanes;
    IML=length(image_idxlist);
    map_radialprofile_f=[];
    map_radialprofile_z=[];
    for ii=1:IML
        eq=image_idxlist(ii);
        im_eq_f=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(eq).filname))),initval.smoothim);
        im_eq_z=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_ZipA,imlist_z(eq).filname))),initval.smoothim);

        radialprofile_f=Build_radial_profile(im_eq_f,initval,dr);
        radialprofile_z=Build_radial_profile(im_eq_z,initval,dr);
       
            profileprops_f=Get_profile_properties(radialprofile_f);
            profileprops_z=Get_profile_properties(radialprofile_z);  
              
        
        if ii==IML            
           round([dr profileprops_f.pk_pos   profileprops_f.pk_val  profileprops_f.plat_val ...                    
                     profileprops_z.pk_pos   profileprops_z.pk_val  profileprops_z.plat_val])
        end
        
        %collect values of plateau and peak
        bleachcurve_f_pk(ii)=profileprops_f.pk_val;
        bleachcurve_f_plat(ii)=profileprops_f.plat_val;
        bleachcurve_z_pk(ii)=profileprops_z.pk_val;
        bleachcurve_z_plat(ii)=profileprops_z.plat_val;
        
         %add to 2D map
         map_radialprofile_f=[map_radialprofile_f; radialprofile_f];
         map_radialprofile_z=[map_radialprofile_z; radialprofile_z];
         map_ratio_fz=map_radialprofile_f./map_radialprofile_z;

        if 0, Plot_stuffA000_163(im_eq_f,im_eq_z,radialmap_f,radialmap_z,radialprofile_f,radialprofile_z); end
    end
    
    
    
    bleachcurve_f_pk=bleachcurve_f_pk/bleachcurve_f_pk(1)*100;
    bleachcurve_z_pk=bleachcurve_z_pk/bleachcurve_z_pk(1)*100;
    bleachcurve_f_plat=bleachcurve_f_plat/bleachcurve_f_plat(1)*100;
    bleachcurve_z_plat=bleachcurve_z_plat/bleachcurve_z_plat(1)*100;
    
    decay_f_pk=Bleachcurvefit(bleachcurve_f_pk);
    decay_z_pk=Bleachcurvefit(bleachcurve_z_pk);  
    decay_f_plat=Bleachcurvefit(bleachcurve_f_plat);
    decay_z_plat=Bleachcurvefit(bleachcurve_z_plat);  
   
    bleachinfo.decay_f_pk(dr)=round(decay_f_pk);
    bleachinfo.decay_z_pk(dr)=round(decay_z_pk);
    bleachinfo.decay_f_plat(dr)=round(decay_f_plat);
    bleachinfo.decay_z_plat(dr)=round(decay_z_plat);
    
 
    if 1
    figure(3);
    subplot(2,2,1); pcolor(map_radialprofile_f'); shading flat
    title('FtsZ'); xlabel('frame'); ylabel('radial pos.');
    subplot(2,2,3); pcolor(map_radialprofile_z'); shading flat
    title('ZipA'); xlabel('frame'); ylabel('radial pos.');   
    subplot(1,2,2); 
        plot(bleachcurve_f_pk, 'b-'); hold on;
        plot(bleachcurve_z_pk, 'r-'); hold on;
        plot(bleachcurve_f_plat, 'c-'); hold on;
        plot(bleachcurve_z_plat, 'm-'); hold on;
        legend('FtsZ-pk', 'ZipA-pk','FtsZ-plat', 'ZipA-plat');
        xlabel('frame'); ylabel('%');
        ylim([0 120]);   
    pause(0.3); 
    [~]=ginput(1); 
    end
  
function  pretracksettings=Sampling_Init(radius,options)
        pretracksettings.radialoversampling=2;
        pretracksettings.angularoversampling=0.7;
        pretracksettings.angularoversampling=1;
        pretracksettings.minradius=0;
        pretracksettings.maxradius=options.radiusexpand*radius;
        pretracksettings.radialoversampling=options.radiusexpand*100/radius;
        switch options.sampling
            case 'radial', 
                pretracksettings=Build_QI_SamplinggridGrid(pretracksettings);
            case 'cross', 
                pretracksettings=Build_Cross_SamplinggridGrid(pretracksettings);
        end
            
function QI=Build_QI_SamplinggridGrid(QI) 
    %Build a radial sampling grid 
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
    QI.radii=radbins;
    
function QI=Build_Cross_SamplinggridGrid(QI) 
    %Build the arms of a cross-style sampling grid 
    crosshalfwidth=10;
    radbinsno=round((QI.maxradius-QI.minradius)*QI.radialoversampling);
    arm_axis=linspace(QI.minradius,QI.maxradius,radbinsno);
    cross_axis=[-crosshalfwidth:crosshalfwidth]'
    
    xx0=repmat(arm_axis,2*crosshalfwidth+1,1);
    yy0=repmat(cross_axis,1,radbinsno);
    
    xxc=xx0;
    yyc=yy0;
    
    angles=[90 180 270];
    for ii=1:3
        [xxr,yyr]=Rotate_Points(0,0,xx0,yy0,angles(ii));
        xxc=[xxc;xxr];
        yyc=[yyc;yyr];
    end
    QI.Y0samplinggrid=xxc;
    QI.X0samplinggrid=yyc;
    QI.angles=cross_axis;
    QI.radii=arm_axis;

function [xxr,yyr]=Rotate_Points(x0,y0,xx,yy,alpha)
%JWJK_A:-------------------------------------------------------------------
%Title Rotation of points around coordinates
%
%Input: coordinates of origin, angle in degrees
%
%Output:
%Refererences: JacobKers 2017, Projects SandroCells-Replicode
%:JWJK_A-------------------------------------------------------------------
if nargin<5
    x0=10;y0=10;
    [xx,yy]=meshgrid(15:20,20:50);
    alpha =30;
end
xx1=xx-x0;                          %relative coords
yy1=yy-y0;
ar=alpha/180*pi;
xx1r=xx1.*cos(ar)-yy1.*sin(ar);     %rotation of relative coords
yy1r=xx1.*sin(ar)+yy1.*cos(ar);
xxr=xx1r+x0;
yyr=yy1r+y0;
if nargin<5
    close all;
    plot(x0,y0,'ro'); hold on;
    plot(xx,yy,'ko'); hold on;
    plot(xxr,yyr,'bo'); hold on;
    axis([0 60 0 60]);
    title('rotation');
    axis equal;
    legend('origin of rotation','points in','points out');
end
   



function [radialprofile,radialmap]=Build_radial_profile(im,initval,dr);
    %build a sampling grid and obtain a profile
    [rr,cc]=size(im);
    
    geometry='table';
    switch geometry
        case 'simple'
             xm=cc/2+0.5;  
             ym=rr/2+0.5;
             radius=0.8*cc/2;
        case 'click'
            figure(4); pcolor(im); shading flat; colormap hot;
            title('click center then edge');
            [rx,ry,but]=ginput(2);  
            xm=rx(1) ;
            ym=ry(1);
            radius=((rx(2)-rx(1))^2+(ry(2)-ry(1))).^0.5;
            [dr xm ym radius]              
            close(gcf);
       case 'table'
           if initval.expi==2
                xm=1.3*(initval.droplet.radius+1);
                ym=1.3*(initval.droplet.radius+1);
                radius =initval.droplet.radius;   %for now, manual
           else
                xm=initval.droplet.xm;
                ym=initval.droplet.ym;
                radius =initval.droplet.radius;   %for now, manual
           end
        case 'trackit'
            radius =initval.droplet.radius;   %for now, manual
            QI=TrackXY_by_QI_Init(im);
            [xm,ym]=TrackXY_by_QI(im,QI,0);
            
            [dr xm ym radius]
            %[~]=ginput(1)
    end     
    %sample
    radius=initval.radiusexpand*radius;
    options.sampling='radial'; %'cross'; %, 'radial';
    options.radiusexpand=initval.radiusexpand;
    radialsampling=Sampling_Init(radius,options);
    [XX,YY]=meshgrid(1:cc,1:rr);
    Xsamplinggrid=radialsampling.X0samplinggrid+xm;
    Ysamplinggrid=radialsampling.Y0samplinggrid+ym;
    radialmap=(interp2(XX,YY,im,Xsamplinggrid,Ysamplinggrid,'Linear',0));
    radialprofile=median(radialmap);
    
    radialprofile=radialprofile-radialprofile(end);  %background subtract
    

function profileprops=Get_profile_properties(profile)
    %Get properties of the radial profile
        %plateau value, mean (0-25% radius)
        %edge value, max (90-110% of radius
        %peak value and location (in units of radius)
        LP=length(profile);
        ax=1:LP;
        sel_pk=find(ax>90&ax<110);
        sel_plat=find(ax<25);
        [pk,idx0]=max(profile(sel_pk));
        platval=mean(profile(sel_plat));
        profileprops.pk_pos=ax(sel_pk(idx0));  %percentage 
        profileprops.pk_val=profile(sel_pk(idx0));
        profileprops.plat_val=platval;      
    dum=1;

 function bleachinfo=Init_Results
    bleachinfo=struct(...
        'decay_f_pk', [],...,
        'decay_z_pk', []);
 
function image_index=Get_driftedZplanes(dr)
    switch dr
        case 1, image_index = [29 99  169 239 309 377 449 519 589 659 729 799 860 949 1016 1086 1159 1229 1299 1369 1439 1509 1584 1654 1724 1794 1864 1938 2008 2078];
        case 2, image_index = [29 99  169 239 309 377 449 519 589 659 729 799 860 949 1016 1086 1159 1229 1299 1369 1439 1509 1584 1654 1724 1794 1864 1938 2008 2078];
        case 3, image_index = [15 85 156 226 298 369 439 509 581 651 722 793 863 935 1005 1075 1147 1217 1288 1359 1430 1501 1571 1644 1714 1784 1856 1926 1997 2068];
        case 4, image_index = [29 99 169 239 309 377 449 519 589 659 729 799 860 949 1016 1086 1159 1229 1299 1369 1439 1509 1584 1654 1724 1794 1864 1938 2008 2078];
        case 5, image_index = [29 99  169 239 309 377 449 519 589 659 729 799 860 949 1016 1086 1159 1229 1299 1369 1439 1509 1584 1654 1724 1794 1864 1938 2008 2078];
        case 6, image_index  = [22 92 162 233 304 374 444 515 585 656 726 798 869 939 1009 1080 1151 1223 1293 1364 1435 1505 1576 1646 1718 1789 1860 1932 2002 2073];
        case 7, image_index  = [22 92 162 233 304 374 444 515 585 656 726 798 869 939 1009 1080 1151 1223 1293 1364 1435 1505 1576 1646 1718 1789 1860 1932 2002 2073];
        case 8, image_index  = [35 105 175 245 315 385 455 527 597 667 740 810 880 950 1023 1094 1165 1235 1307 1377 1445 1516 1587 1657 1727 1798 1870 1941 2012 2083];
        case 9, image_index  = [121 173 223 291 262 433 503 574 645 715 786 857 928 998 1069 1140 1211 1282 1352 1423 1494 1565 1636 1707 1778 1849 1919 1990 2061];
        case 10, image_index  = [666 719 790 861 931 1002 1073 1144 1214 1285 1355 1427 1498 1569 1640 1711 1781 1852 1923 1994 2064];
        case 11, image_index  = [666 719 790 861 931 1002 1073 1144 1214 1285 1355 1427 1498 1569 1640 1711 1781 1852 1923 1994 2064];
        case 12, image_index  = [268 298 368 439 510 580 652 722 792 862 934 1004 1075 1146 1218 1288 1359 1430 1501 1572 1642 1713 1785 1856 1926 1997 2068];
        case 13, image_index  = [958 1004 1074 1144 1216 1285 1356 1427 1498 1569 1640 1711 1783 1583 1924 1995 2066];

    end

    function initval=Set_Data(expi,dr);
switch expi
    case 0
        initval.expi=0;
        %local test images with bundles  ; to be expanded to 13
        droplet.no=[1 2 3 4 5 6 7 8 9 10 11];
        droplet.code=[52725 52746 52752 52737 ...
                      52746 52752 52752 52725 ...
                      52737 52737 52737];
        all_top=[10 13 10 32 ... 
                     10 14 7  3 ... 
                     8  5 10];
        all_eq=[100 90 75 105 ...
                    37  38 35  17 ... 
                    32  25  25 ];
       all_bot=[178 154 142 178 ... 
                     74  63  64  33 ... 
                     56  40  39];
    clicks=[
         1.0000  145.8799  146.8473  105.2360
        2.0000  129.3630  131.6395   89.5218
        3.0000  105.7341  103.8210   82.8221
        4.0000  116.3188  117.0419   94.9770
        5.0000   49.9436   49.3138   38.5841
        6.0000   38.8897   38.8539   30.1125
        7.0000   43.7232   44.7709   34.4719
        8.0000   29.4990   27.3091   17.1662
        9.0000   37.3690   36.3602   28.1648
       10.0000   28.8026   27.1391   14.3916
       11.0000   28.9286   26.3512   18.8177]; 
   
        droplet.top=all_top;
        droplet.eq=all_eq(dr);
        droplet.bot=all_bot(dr);
   
        droplet.allno=round(clicks(:,1))';  %expand to 13  
        droplet.thisno=dr;  %expand to 13  
        droplet.xm=clicks(dr,2)';
        droplet.ym=clicks(dr,3)';   
        droplet.radius=clicks(dr,4)';
        
        %from: M:\tnw\bn\cd\Shared\Federico\Papers\FtsZ_Droplets\Fig1    
        initval.indir='C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_05_27 PaperFig1\';
        initval.dir_FtsZ=[initval.indir,'droplet',num2str(dr),'_',num2str(droplet.code(dr)),'_FtsZ\'];
        initval.dir_ZipA=[initval.indir,'droplet',num2str(dr),'_',num2str(droplet.code(dr)),'_ZipA\']; 
        initval.savedir='C:\Users\jkerssemakers\Dropbox\CD_Data_out\2019_Fede\2019_BundleRatios\';
        initval.savename='exp_0_bundles_bleached';
   case 1
        initval.expi=1;
        %control without bundles, see email fede 17-5-19
        %from: M:\tnw\bn\cd\Shared\Federico\Data\19-05-16 calibration
        droplet.code=[61949 62005 62014 62014 62021];
        clicks=[...  
            1.0000  107.3637  101.1157   91.0000
            2.0000  165.5939  169.8494  134.0000 
            3.0000  107.7568  105.6852   92.0000 
            4.0000  102.5842  101.4728   83.0000 
            5.0000  136.5417  136.0069  110.0000];
        all_top=[7 7 11 20 7];
        all_eq=[82 133 87 118 110];
        all_bot=[143 221 153 152 189];
        
        droplet.allno=round(clicks(:,1))';  %expand to 13 
        droplet.thisno=dr;  %expand to 13 
        droplet.xm=clicks(dr,2)';
        droplet.ym=clicks(dr,3)';   
        droplet.radius=clicks(dr,4)';
        droplet.top=all_top(dr);
        droplet.eq=all_eq(dr);
        droplet.bot=all_bot(dr);
        initval.indir='C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_05_27 Paper No bundles\';
        initval.dir_FtsZ=[initval.indir,'drop',num2str(dr),'_FtsZ_',num2str(droplet.code(dr)),'\'];
        initval.dir_ZipA=[initval.indir,'drop',num2str(dr),'_ZipA_',num2str(droplet.code(dr)),'\']; 
        initval.savedir='C:\Users\jkerssemakers\Dropbox\CD_Data_out\2019_Fede\2019_BundleRatios\';
        initval.savename='exp_1_nobundles_no_bleach';
    case 2 %non-bleached bundles, from C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_06_05 Nonbleached Bundles
         %this data contains multiple droplets per image
        initval.indir='C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_06_05 Nonbleached Bundles\';
        initval.dir_FtsZ=initval.indir;
        initval.dir_ZipA=initval.indir; 
         initval.savedir='C:\Users\jkerssemakers\Dropbox\CD_Data_out\2019_Fede\2019_BundleRatios\';
        initval.savename='exp_2_bundles_notbleached';
        initval.expi=2;
        droplet.allno=1:36;  %expand to 13 
        droplet.thisno=dr;  %expand to 13 
        dropletinfo=Get_nonbleached_dropletinfo(dr);
        %Droplet	Image	XM	YM	Radius	BX	BY	Width	Height
        droplet.imno=dropletinfo(2);
        droplet.imname=309+droplet.imno;
        droplet.xm=dropletinfo(3);
        droplet.ym=dropletinfo(4);
        droplet.radius=dropletinfo(5);
        dum=1;
        
        
   
    case 3  %time evolution of droplets, data 2016_Fede\2019_05_29 PaperFig2
        initval.expi=2;
        clicks=[
            1.0000   74.2243   73.8580   61.4755
            2.0000   83.8833   82.6128   72.3044
            3.0000   32.8871   31.9484   26.5045
            4.0000   69.0791   70.9660   66.9097
            5.0000   71.4017   75.6994   69.1875
            6.0000   57.9409   61.7733   52.8148
            7.0000   61.2688   61.7218   54.9217
            8.0000   86.0346   85.5574   82.9392
            9.0000   23.4355   19.7033   10.6501
           10.0000   34.9194   29.8648   20.6040
           11.0000   35.6221   34.3210   19.4655
           12.0000   31.2204   41.6897   24.5634
           13.0000   33.4677   34.5224   20.6129];
        droplet.allno=round(clicks(:,1))';  %expand to 13 
        droplet.thisno=round(clicks(dr,1))';  %expand to 13
        droplet.xm=clicks(dr,2)';
        droplet.ym=clicks(dr,3)';   
        droplet.radius=clicks(dr,4)';
        droplet.zplanes=Get_driftedZplanes(dr);
        initval.indir='C:\Users\jkerssemakers\CD_Data_in\2016_Fede\2019_05_29 PaperFig2\';
        initval.dir_FtsZ=[initval.indir,'drop',num2str(droplet.no(dr)),'_FtsZ\'];
        initval.dir_ZipA=[initval.indir,'drop',num2str(droplet.no(dr)),'_ZipA\'];     
        initval.savedir='C:\Users\jkerssemakers\Dropbox\CD_Data_out\2019_Fede\2019_BundleRatios\';
        initval.savename='exp_3_bundles_bleachseries';
end
initval.radiusexpand=1.2;
initval.smoothim=1;
initval.droplet=droplet;
        
function dropletinfo=Get_nonbleached_dropletinfo(dr);
%Droplet	Image	XM	YM	Radius	BX	BY	Width	Height
alldropletinfo=[...
            1            1       256.14       147.66        60.25          194           88          122          119
            2            2       205.77       191.23        29.25          174          162           60           57
            3            2       281.82       288.58         19.5          263          268           38           40
            4            3       256.87       49.343           23          234           25           46           46
            5            4        173.1       321.42         67.5          104          255          137          133
            6            4       338.27       288.78        65.25          272          224          131          130
            7            5       288.52       302.89           30          258          274           61           59
            8            5       387.32       328.71         28.5          359          300           55           59
            9            6       108.72       277.66           61           46          218          123          121
           10            7       256.89       251.22        79.25          178          172          159          158
           11            8       366.81       108.46        44.75          322           63           90           89
           12            9       187.06       154.69        25.25          162          129           50           51
           13            9       391.11       375.98           32          359          344           65           63
           14            9       159.61       409.97           16          142          394           33           31
           15           10        108.9       310.17        43.25           66          266           86           87
           16           11       92.477       107.34           61           30           37          122          122
           17           12       132.34       152.06        20.25          111          131           41           40
           18           13       302.46        164.3           83          220           84          166          166
           19           14       276.31       258.41          170          108           91          338          342
           20           15       401.21       108.43         30.5          371           80           60           62
           21           15       451.51       294.87           38          415          257           75           77
           22           15       320.37       424.98         43.5          277          381           87           87
           23           16       231.27       208.64           30          200          178           60           60
           24           17       422.37       203.55         54.5          368          148          107          111
           25           17       101.19       318.81        74.25           27          245          149          148
           26           18       270.87       266.82           56          215          210          112          112
           27           19       68.306       60.583        31.25           39           27           61           64
           28           19       337.32       194.26         45.5          292          149           91           91
           29           19       437.85        276.1        34.75          402          242           71           68
           30           20       147.23        157.8        64.75           82           93          129          130
           31           20       282.16        383.9        49.75          232          334          100           99
           32           21       226.14       113.62         46.5          180           67           92           94
           33           22       276.29       264.14         40.5          234          224           82           80
           34           23       254.76        257.5        59.25          194          199          120          117
           35           24       380.73       267.98        43.25          339          224           86           87
           36           25       277.17       222.56        82.75          194          138          163          168];
dropletinfo=alldropletinfo(dr,:);


function [im_eq_f,im_eq_z]=Fetch_imagepair(initval,dr);
    %load from differently organized data dirs
    if initval.expi==0|...  droplet per dir
       initval.expi==1
            [imlist_f,~]=Scroll_ImageDirs(initval.dir_FtsZ  ,'*.tif');
            [imlist_z,~]=Scroll_ImageDirs(initval.dir_ZipA  ,'*.tif');    
            eq=initval.droplet.eq;  %'eq' points to the right image index    
            im_eq_f=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(eq).filname))),initval.smoothim);
            im_eq_z=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_ZipA,imlist_z(eq).filname))),initval.smoothim);
            
            
    end
    if initval.expi==2  %multiple droplets per single plane
        [imlist_f,~]=Scroll_ImageDirs(initval.dir_FtsZ  ,'*1.tif');
        [imlist_z,~]=Scroll_ImageDirs(initval.dir_ZipA  ,'*0.tif');
        imno=initval.droplet.imno;
        im_eq_f_large=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_FtsZ,imlist_f(imno).filname))),initval.smoothim);
        im_eq_z_large=JKD2_IM_smoothJK(double(imread(strcat(initval.dir_ZipA,imlist_z(imno).filname))),initval.smoothim);
        lox=round((initval.droplet.xm-1.3*initval.droplet.radius));
        hix=round((initval.droplet.xm+1.3*initval.droplet.radius));
        loy=round((initval.droplet.ym-1.3*initval.droplet.radius));
        hiy=round((initval.droplet.ym+1.3*initval.droplet.radius));
        im_eq_f=im_eq_f_large(loy:hiy,lox:hix);
        im_eq_z=im_eq_z_large(loy:hiy,lox:hix);
        dum=1;
    end