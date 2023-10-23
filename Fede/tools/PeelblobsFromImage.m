function AllSpotProps=PeelblobsFromImage(im,Psf,ChipFract,RelChangeStop,sho);
%JWJK_C:-------------------------------------------------------------------
%Title: Multi-peak fitter
%
%Summary: This function subtracts 2D Gaussians of fixed width from an image until a stop criterion
%is met. the gaussians can then be used for reconstructing the curve in
%main components, for example defined by optical separation.

%Output: %AllSpotProps=[spotcount Peak Xpos Ypos Psf ThisSpotFraction(spotcount) CoveredFraction(spotcount) RelChange]];  
%
%Project: BN_CD16_Greg, Fabai ; JacobKers 2016
%:JWJK_C-------------------------------------------------------------------

   
stopit=0;
PeelIm=im;
BuildIm=0*im;
spotcount=0;
CoveredFraction=[];
SpotPeak=[];
AllSpotProps=[];
close all;
 if sho
        pcolor(PeelIm'); shading flat, colormap bone;
        axis equal; axis tight; axis off; hold on;
        caxis([min(im(:)) max(im(:))]);
        title('residu');
        pause(0.2);
        [~]=ginput(1);
end



while ~stopit
    [~,Xpos]=max(max(PeelIm));
    [Peak,Ypos]=max(max(PeelIm'));                  
    SpotIm= ChipFract*Peak*TwoDGaussNormPeak(im,Xpos,Ypos,Psf);    
    PeelIm=PeelIm-SpotIm;
    BuildIm=BuildIm+SpotIm;
    spotcount=spotcount+1;
    CoveredFraction(spotcount)=sum(BuildIm(:))/sum(im(:));
    ThisSpotFraction(spotcount)=sum(SpotIm(:))/sum(im(:));
     
    if spotcount>1 %check progress
        RelChange=(CoveredFraction(spotcount)...
                  -CoveredFraction(spotcount-1))./...
                   CoveredFraction(spotcount);
               if (RelChange<RelChangeStop) | (CoveredFraction(end)>1),...
                       stopit=1; 
               end
                             
    else
        RelChange=1;
    end
    
    
    AllSpotProps=[[AllSpotProps];...
        [spotcount Peak Xpos Ypos Psf ThisSpotFraction(spotcount) CoveredFraction(spotcount) RelChange]]; 
    
    if sho
%         subplot(2,2,1); pcolor(im'); shading flat, colormap bone;
%         axis equal; axis tight; axis off; hold on;
%         title('original')
%         subplot(2,2,2); pcolor(BuildIm'); shading flat, colormap bone;
%         axis equal; axis tight; axis off; hold on;
%         title(strcat('Reconstructed Using ', num2str(spotcount), ' Spots'));
%         subplot(2,2,3); 
        pcolor(PeelIm'); shading flat, colormap bone;
        axis equal; axis tight; axis off; hold on;
        caxis([min(im(:)) max(im(:))]);
        title('residu');
        pause(0.2);
        [~]=ginput(1);
    end
   
end
close(gcf);

%CleanSpotProps=CleanSpots(AllSpotProps,im,Psf);
%1 spotcount Peak Xpos Ypos Psf ThisSpotFraction(spotcount) RelChange]
if sho 
    PlotProps=AllSpotProps;
        figure;     
        pcolor(im); shading flat, colormap bone; hold on;
        perc=num2str(round(100*PlotProps(end,7)));
            title(strcat('Overlay covering',perc,'percent'));
        scale=24/max(PlotProps(:,6));
        [LS,~]=size(PlotProps);
        for sp=1:LS
            mrksize=ceil(PlotProps(sp,6)*scale);
            x=PlotProps(sp,3);
            y=PlotProps(sp,4);
            
            plot(x,y,'ro','MarkerSize',max([mrksize 1]),'LineWidth',2);
            hold on; 
            text(x+1,y+1,num2str(sp),'BackgroundColor','w');
            %axis equal;
        end
        
        [LS,~]=size(PlotProps);
        for sp=1:LS
            x0=PlotProps(sp,3);
            y0=PlotProps(sp,4);
            sel=find(PlotProps(:,1)~=sp);
            otherspots=PlotProps(sel,:);
            otherx=otherspots(:,3);
            othery=otherspots(:,4);
            rr=((otherx-x0).^2+(othery-y0).^2).^0.5;
            near_ones=find(rr<2*Psf);
            pairsX=[otherx(near_ones)' ; 0*otherx(near_ones)'+x0];
            pairsY=[othery(near_ones)' ; 0*othery(near_ones)'+y0];
            plot(pairsX,pairsY,'r', 'LineWidth',2); hold on;               
        end
        [~]=ginput(1);
end

        
