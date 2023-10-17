function CleanSpotProps=F006_CleanSpots(AllSpotProps,im,Psf);
%This function removes spots 
CleanSpotProps=[];
[rr,cc]=size(im);
[YY,XX]=meshgrid(1:cc,1:rr);

[LS,~]=size(AllSpotProps);
%pcolor(im); shading flat, colormap bone; hold on;
        for sp=1:LS
            x=AllSpotProps(sp,3);
            y=AllSpotProps(sp,4);
            rr=((XX-y).^2+(YY-x).^2).^0.5;
            sel=find((im==nanmedian(im(:)))&(rr<Psf));
            if isempty(sel)
                CleanSpotProps=[CleanSpotProps; AllSpotProps(sp,:)];
              %  plot(x,y,'bo','MarkerSize',4,'LineWidth',2);
            else
               % plot(x,y,'rx','MarkerSize',4,'LineWidth',2);
                %plot(YY(sel),XX(sel),'yo');
            end
        end
