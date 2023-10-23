function [fluo,BW_pic]=FF_Basic_Fluorescence(FL,sigma);
%This function returns some fluorescent properties, based on simple
%assumption of the fluorescent pattern of the bacterium

%-------------------------------------
%Note: all 'levels' beyond dark are calculated from this dark level
%------------------------------------------
close all
[r,c]=size(FL);
fluo.counts_all=sum(FL(:));

%1 First, we make estimates on intensity and noise of the background (far outside
%the lipo).'local background' is defined as the average of the outer two image lines'
fluo.level_dark=(mean(mean(FL(1:2,:)))+mean(mean(FL(r-1:r,:))))/2;


%2) estimate dark (camera) noise via the spread in the difference between
%neighbouring pixels
diftop=FL(1:5,2:end)-FL(1:5,1:end-1); 
difbot=FL(r-4:r,2:end)-FL(r-4:r,1:end-1);
dif=[diftop(:);  difbot(:)];
fluo.noise_dark=std(dif)/2^0.5;

%define as 'fluorescence' those pixels sufficiently above the darklevel.
%Note this may not be representative for the outline of the bacterium,
%since there is some blurring and we want to measure all fluorescence
fluotreshold=fluo.level_dark+sigma*fluo.noise_dark;
FLbc=FL-fluotreshold;
backsel=find(FL<fluotreshold);
fluo.level_fluotreshold=fluotreshold;
FLbc(backsel)=0;

%a) summed intensities (minus background)
fluo.counts_fluorescence=sum(FLbc(:));       %total represents total counts

%make a picture representing the liposome, to show if the selected
%area cover realistic parts; store these indices for later use
fluo.wherefluo=find(FL>fluotreshold);
fluo.wheredark=find(FL<=fluotreshold);
fluo.area=length(fluo.wherefluo);

BW_pic=0*FL;
BW_pic(fluo.wherefluo)=1;

fluo.counts_justliporegion=sum(sum((FLbc.*BW_pic)));       %total represents total counts
fluo=orderfields(fluo);




