function [flag,cleanprf]=prf_outlier_flag(prf,tolerance,sigchange,how,sho);
 %JWJK_C:-------------------------------------------------------------------  
    %this function is meant to find a representative value for a standard
    %deviation in a heavily skewed distribution (typically, flat prf with
    % %peaks). It calculates the standard deviation and average the prf;
    % Based on these, outliers are determined and excluded for a new calculation
    % of average and SD; this is repeated until sigma does not change anymore too much
    % This is repeated until the new sigma does not change much anymore
    %output: positions of outliers. Jacob Kers 2013 and before

    %input (suggested):
        % data: single data array
        % tolerance: beyond how many sigmas is considered outlier (3)
        % sigchange: stop iteration if relative decrease of sigma is less (0.7)
        % how: consider positive outliers, or all ('all' /'positive'
        % sho: (for demo only) show intermediate graphs (0)

    %output: 
        %flags: positions of outliers
        %cleandata: data w/o outliers
      %Reference: Cees Dekker Lab, 
      %code designed & written Jacob Kerssemakers 2016 
    %:JWJK_C-------------------------------------------

binz=50;

if nargin<5  %For testing/demo purposes
    close all
    prf=prf_make_demo_curves('multipeaks');;
    tolerance=2;
    sigchange=0.7;
    how='positive';
    sho=1;
    plot(prf,'o-');
    binz=20;
end

sigma=1E20;            %at start, use a total-upper-limit 
ratio=0;
ld=length(prf);
flag=ones(ld,1);  %at start, all points are selected
cleanprf=prf;
while ratio<sigchange     %if not too much changes anymore; the higher this number the less outliers are peeled off.
    sigma_old=sigma;
    selc=find(flag==1);
    prf(flag==1); 
    ls=length(selc);
    if ls>0
        av=nanmedian(prf(selc));       %since we expect skewed distribution, we use the median iso the mea     
        sigma=nanstd(prf(selc));
        ratio=sigma/sigma_old;
        switch how
            case 'positive',  flag=(prf-av)<tolerance*sigma;     %adjust outlier flags
            case 'all',  flag=abs(prf-av)<tolerance*sigma;     %adjust outlier flags  
        end
        %plot menu------------------  
        if sho==1
            close all;
            cleanprf=prf(selc); 
            hx=(min(cleanprf):(range(cleanprf))/binz:max(cleanprf));   %make an axis
            sthst=hist(cleanprf,hx);
            bar(hx,sthst);
            title('Histogram');
            [xpos,~]=ginput(1)
            pause(0.5);     
        end
        cleanprf=prf(selc);
    else
        ratio=sigchange; %force stop
        cleanprf=prf;
    end
end
 
hx=(min(cleanprf):(range(cleanprf))/binz:max(cleanprf));   %make an axis
sthst=hist(cleanprf,hx);





