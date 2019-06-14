        function Plot_stuff163(im_eq_f,im_eq_z,radialmap_f,radialmap_z,radialprofile_f,radialprofile_z)
        % plotting per loop       
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
        subplot(2,2,1);
        plot(radialprofile_f,[clr,'-'], 'LineWidth', 1);  hold on;    
        title('FtsZ')
        xlabel('radial pos, % of radius');
        ylabel('counts per profile');
        ylim([0 8000]);
        subplot(2,2,2);
        plot(radialprofile_z,[clr,'-'], 'LineWidth', 1);  hold on;
        title('ZipA')
        xlabel('radial pos, % of radius');
        ylabel('counts per profile');
        ylim([0 8000]);

        subplot(2,1,2);
        plot(radialratio,[clr '-'], 'LineWidth', 2);  hold on;
        title('Ratio');
        xlabel('radial pos, % of radius');
        ylabel('ratio');
        ylim([0 8]);

        pause(0.3); [~]=ginput(1);
        dum=1;