function Plot_Save_stuff_A000_line116(im_eq_f,im_eq_z,radialmap_f,radialmap_z,radialprofile_f,radialprofile_z,initval);
        
        LP=length(radialprofile_f);
        radialaxis=initval.droplet.radius*(1:LP)'/100;
        radialaxis_perc=(1:LP)';
        FZ_ratio=radialprofile_f./radialprofile_z;
        
        figure(1);
        subplot(3,2,1); pcolor(im_eq_f); colormap hot; shading flat;
        title('FtsZ'); axis off, axis equal
        subplot(3,2,2); pcolor(im_eq_z); colormap hot; shading flat;
        title('ZipA'); axis off, axis equal
        subplot(3,2,3); pcolor(radialmap_f); colormap hot; shading flat;
        xlabel('radial pos, % of radius');
        subplot(3,2,4); pcolor(radialmap_z); colormap hot; shading flat;
        xlabel('radial pos, % of radius');
        subplot(3,2,5); plot(radialprofile_f);
        xlabel('radial pos, % of radius');
        ylabel('counts');
        subplot(3,2,6); plot(radialprofile_z); 
        xlabel('radial pos, % of radius');
        ylabel('counts');

        figure(2);
        switch initval.expi
            case 0, clr='b';
            case 1, clr='r';
            case 2, clr='k';
        end
        subplot(1,3,1);
        plot(radialprofile_f,[clr,'-'], 'LineWidth', 1);  hold on;    
        title('FtsZ')
        xlabel('radial pos, % of radius');
        ylabel('counts per profile');
        ylim([0 8000]);
        subplot(1,3,2);
        plot(radialprofile_z,[clr,'-'], 'LineWidth', 1);  hold on;
        title('ZipA')
        xlabel('radial pos, % of radius');
        ylabel('counts per profile');
        ylim([0 8000]);
        
        subplot(1,3,3);
        
        plot(FZ_ratio,[clr,'-'], 'LineWidth', 1);  hold on;
        title('Ratio')
        xlabel('radial pos, % of radius');
        ylabel('counts per profile');
        %ylim([0 8000]);
        pause(0.05); 
        %% saving per-droplet results   
        dr=initval.droplet.thisno;
        dropletsavename=[initval.savename, 'droplet',num2str(dr,'%02.0f'),'_results.mat'];
        save([initval.savedir,dropletsavename],...
            'initval',...
            'im_eq_f',...
            'im_eq_z',...
            'radialaxis',...
            'radialaxis_perc',...
            'radialmap_f',...
            'radialmap_z',...
            'radialprofile_f',...
            'radialprofile_z',...
            'FZ_ratio');
        figure(1);
        picsavename=[initval.savename, 'droplet',num2str(dr,'%02.0f'),'_results'];
        saveas(gcf,[initval.savedir,picsavename], 'jpeg');
        dum=1;
    end