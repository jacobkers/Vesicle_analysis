function A001_ReadImageStacks
%this function applies avaraged-out Fourier analysis to collection of images
%Jacob Kers 2016

initval.micronsperplane=0.5;
initval.Psf=15;
close all;
if ismac, DirSep='/';else DirSep='\';end;
NumberOfColorChannels=1;

%% some setting up
  %specifying zoomin on the fourier plot
switch 1    
  case 1
        initval.exp_label='droplet_in_trap_4' ; 
        initval.mainpath='D:\jkerssemakers\_Data\CD\2016_Fede\';
        initval.subdir='droplet_in_trap_4\Stacks' ; 
  end
      
%% find all files in the subdirectory that contain the 'filestring' template
    %and return a list of them (including names, path)  
    WorkDir=strcat(initval.mainpath,initval.subdir,DirSep);
    filelist=Scroll_ImageDirs(WorkDir,'*.tif');
    
%% load stacks, separate colors
   
    [~,ST]=size(filelist);  
     AllCounts=[];
     HeaderRow1=[]; HeaderRow2=[];
     for st_ii=1:ST    %all stacks         
        %1 ) Get info on stack sizes
            dirname=filelist(st_ii).dirname;
        filname=filelist(st_ii).filname;
        firstplane=double(imread(strcat(dirname,DirSep,filname),'Index',1));
        info = imfinfo(strcat(dirname,DirSep,filname));    
        [rr,cc]=size(firstplane);
        [allplanes,~]=size(info);  
        planespercolor=floor(allplanes/NumberOfColorChannels);               
        CountsPerplane=zeros(planespercolor,NumberOfColorChannels);
        %2) work all images
        for planeindex=1:planespercolor       %all planes
            if mod(planeindex,20)==0, disp(strcat(num2str(planespercolor-planeindex+1),'images and',num2str(ST-st_ii+1), 'stacks to go')); end      
 
            channelindex=1+(planeindex-1)*NumberOfColorChannels;
            for clr=1:NumberOfColorChannels
                im=double(imread(strcat(dirname,DirSep,filname),'Index',channelindex-1+clr));  
                %do something to this image--------------------------------
                
                
                %----------------------------------------------------------
                CountsPerplane(planeindex,clr)=sum(im(:));               
                if 0
                    subplot(2,2,clr); pcolor(im); shading flat; axis equal; colormap bone;
                    title(strcat('Color', num2str(clr),'Plane',num2str(planeindex)));
                    pause(0.01); 
                end
            end                     
        end  
        %subplot(2,1,2)
                
         plot(CountsPerplane,'-'); hold on;
         title(initval.exp_label);
         ylabel('totalcounts');
         xlabel('planeindex');
         pause(0.1); 
        
        [rC,~]=size(CountsPerplane);
        [rA,cc]=size(AllCounts);
        if rC<rA
            dC=rA-rC;
            AllCounts=[AllCounts [CountsPerplane; zeros(dC,2)]];
        else
            if rC>rA
                dC=rC-rA;
                AllCounts=[[AllCounts; zeros(dC,cc)] CountsPerplane];
            else
                 AllCounts=[AllCounts CountsPerplane];
            end
        end
        
       
        for clr=1:NumberOfColorChannels
        HeaderRow1=[HeaderRow1 {filname}];
        HeaderRow2=[HeaderRow2 {strcat('Color',num2str(clr))}];
        end
     end
     
     Outdata=[(1:planespercolor)' ...
              initval.micronsperplane*(1:planespercolor)' ...
              AllCounts];
     HeaderRow1=[{'Stacks'}, {'Stacks'}, HeaderRow1];
     HeaderRow2=[{'Plane'}, {'Height'}, HeaderRow2];
     
     %%save data to main dir, excel with headers
     SaveName=strcat('_A001_Results_Z_Stackcounts',initval.exp_label);
     xlswrite(strcat(WorkDir,DirSep,SaveName,'.xlsx'),HeaderRow1,'Sheet1','A1');
     pause(5);
     xlswrite(strcat(WorkDir,DirSep,SaveName,'.xlsx'),HeaderRow2,'Sheet1','A2');
     %xlswrite(strcat(initval.mainpath,DirSep,SaveName,'.xlsx'),Outdata,'Sheet1','A3');
     xlswrite(strcat(WorkDir,DirSep,SaveName,'.xlsx'),Outdata,'Sheet1','A3');
     save(strcat(WorkDir,DirSep,SaveName,'.mat'),'Outdata','HeaderRow1', 'HeaderRow2');
     saveas(gcf,strcat(WorkDir,DirSep,'_A040_Results_Z_Stackcounts',initval.exp_label,'.jpg'));

     
        
        
  
     
 
     
     
     

