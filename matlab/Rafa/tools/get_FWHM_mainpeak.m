function [FWHM]=get_FWHM_mainpeak(histo,bins);
    %blow up
    binstep=median(diff(bins));
    LB=length(bins);
    minbin=bins(1); maxbin=bins(end);
    bins_ip=linspace(minbin,maxbin,50*LB);
    histo_ip=interp1(bins, histo,bins_ip);
    histo_ip_smz=(JKD1_PRF_smooth(histo_ip',50))';
    
    %find max
    [pk_val, pk_idx]=max(histo_ip_smz);
    
    %find halfway up edges    
    Lp=length(histo_ip_smz);
    lix=1:pk_idx; 
    rix=pk_idx+1:Lp;
    HM=pk_val-pk_val/2;
    [~,li]=min(abs(histo_ip_smz(lix)-HM));
    [~,ri0]=min(abs(histo_ip_smz(rix)-HM)); 
    %set limits
    if isempty(ri0),ri=Lp; else ri=ri0+pk_idx;    end
    if isempty(li), li=1; end
    FWHM=bins_ip(ri)-bins_ip(li);
     if 0
        close all;
        plot(bins, histo); hold on,
        plot(bins_ip, histo_ip_smz); hold on,
        plot([bins_ip(li) bins_ip(ri)],[histo_ip_smz(ri) histo_ip_smz(li)], 'ro-');
        [~]=ginput(1);
     end
    if isempty(FWHM) 
        close all;
        plot(bins, histo); hold on,
        plot(bins_ip, histo_ip_smz); hold on,
        plot([bins_ip(li) bins_ip(ri)],[histo_ip_smz(ri) histo_ip_smz(li)], 'ro-');
        [~]=ginput(1);
        FWHM=NaN; 
    end
 
    
  