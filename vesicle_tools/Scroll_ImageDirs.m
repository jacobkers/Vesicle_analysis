function [pic_list,filleddir_list]=Scroll_ImageDirs(impth,SearchTemplate)
     %This function generates a list of full_pathfilenames containing the right
     %string
     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %disp('start scan....');
    pic_list=struct('dirname',[],'filname',[]);
    filleddir_list=struct('dirname',[]);
    progdir=pwd;    
    if ismac, PathSep=':';else PathSep=';';end;
    p = genpath(char(impth)); 
    %String cotaining all (sub)dirs
    lp=length(p);
    dircount=0;
    filleddircount=0;
    filcount=0;
    oldi=1; nwi=oldi;
    while dircount<lp                        %separate out directory names
        dircount=dircount+1;
        nwi=nwi+1;       
        str=char(p(dircount));
        if strcmp(str,PathSep)              %This is one directory name
            dirnm=p(oldi:nwi-2);            
            cd(dirnm);                       %read the proper file names in this directory
            FilNames=dir(SearchTemplate);
            lm=length(FilNames); 
            if lm>0
                filleddircount=filleddircount+1;
                filleddir_list(filleddircount).dirname=dirnm;
            end
            for j=1:lm 
                filcount=filcount+1;
                pic_list(filcount).dirname=dirnm;
                pic_list(filcount).filname=FilNames(j).name ;      
            end
            oldi=nwi;
            cd(progdir);
        end  
    end  