function outpth=swap_path(inpth)
%This function is a simple swap to work with lokal dropboxes on different
%machines and not change too much old code.
%I use two kind of main paths I use; 
%one contains 'CD_Data_in'; %for data-in paths, should be next to Dropbox
%all others contain 'Dropbox'; 

%Jacob Kers, 2019
clc
if nargin<1
    inpth='D:\flappaflapa\CD_Data_in\2016_Sandro'; 
    inpth='D:\trala\Dropbox\BN_recent\BN_All_14_Matlab_Code\JK_CleanTools';
    inpth='D:\jkerssemakers\Dropbox\BN_recent\BN_All_14_Matlab_Code\JK_CleanTools';
end

%% check what path
    outpth=Patch_Path(inpth,'Dropbox');
    outpth=Patch_Path(outpth,'CD_Data_in');    
    
    function outpth=Patch_Path(inpth,commondir); 
    %% find the local path above dropbox
    thispth=char(pwd);
    dropboxname='Dropbox';
    Ld=length(dropboxname);
    k1 = strfind(thispth,char(dropboxname));
    if ~isempty(k1)                      %the Dropbox path
        upperpath=thispth(1:k1-1);       %path above dropbox
        k2 = strfind(inpth,char(commondir));
        if ~isempty(k2)
            lowerpath=inpth(k2:end);
            outpth=[upperpath lowerpath];
        else
            outpth=inpth;                %no idea
        end
    else
       outpth=inpth;                %no idea
    end

    



