function [cXout,cYout]=xy_sort_contour(cXin,cYin); 
    %sort points by mutual distance    
    cxbuf=cXin(2:end);
    cybuf=cYin(2:end);
    cXout=[cXin(1)];
    cYout=[cYin(1)];
    cnt=0;
    stopit=0;
        while length(cXout)<length(cXin)&(stopit==0);  
            cnt=cnt+1;
            curx=cXout(end);
            cury=cYout(end);
            dd=((cxbuf-curx).^2+(cybuf-cury).^2).^0.5; %distance to others
             
            [dm,im]=min(dd);  curidxes=1:length(dd);
            dm_all(cnt)=dm;
            d_typical=nanmedian(dm_all);
            if (dm<10*d_typical)            
                cXout=[cXout ;cxbuf(im)];      %add
                cYout=[cYout ; cybuf(im)];
                cxbuf=cxbuf(curidxes~=im);     %peel off
                cybuf=cybuf(curidxes~=im);
            else
                stopit=1;
            end
            
        end
             cXout=[cXout ;cXout(1)];      %add
             cYout=[cYout ; cYout(1)];
  
    
