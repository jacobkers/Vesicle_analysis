function x=SymCenter(prf);
    %this function find the symmetry center of an array
    mp=nanmean(prf);
    sel=find(isnan(prf)); prf(sel)=mp;  %padding nans
    fw=prf-nanmean(prf);             %forward
    rv=fliplr(prf)-nanmean(prf);     %reverse
    d=real(ifft(fft(fw).*conj(fft(rv))));
    ld=ceil(length(d)/2);
    d=[d(ld+1:length(d)) d(1:ld)]';   %swap first and second half 
    [val,x]=max(d);
    x=(subpix_step(d)+length(prf)/2)/2;
    if 0
    figure(5);
    subplot(2,1,1);
    plot(prf);
    
    subplot(2,1,2);
    plot(d);
    
    [~]=ginput(1);
    
    close(gcf); 
    end
  
 function x=subpix_step(d);
    %this function performs a subpixel step by parabolic fitting
    hf=3; ld=length(d);  xs=[1:1:ld]';   [val,x]=max(d);  %uneven hf
    lo=max([x-hf 1]); hi=min([x+hf ld]);  %cropping
    ys=d(lo:hi); xs=xs(lo:hi);
    prms=polyfit(xs,ys,2); x=-prms(2)/(2*prms(1));