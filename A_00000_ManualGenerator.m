function A_00000_ManualGenerator
% 'Use this section for a Quicksheet'
%------------------------------------------------------------------
    %This quicksheet was made with MatlabFilesAutoQuicksheet
    %This tool is intended to build an auto-updating quicksheet for use of custom code packages 
    % The program searches all m.files in a project directory for any
    %piece of text between two taglines (without the 'minus signs) :
    % 'Use-this-section-for-a-Quicksheet' 
    % 'End-of-Quicksheet-section'
    %These lines are used to indicate important sections to adjust settings
    %etc. or to find back places where data is saved.

    % Disclaimer: the associated custom code was developed for scientific use. 
    % For efficient use of developing time, limited time is spent on user interfaces. 
    % Therefore, the user is supposed to have reasonable knowledge of Matlab code 
    % and an understanding of the functions and algorithms, especially those
    % where the user is asked to adjust settings as below. Jacob Kerssemakers 2014 
%------------------------------------------------------------[JK14]
% 'End of Quicksheet section'

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clc
clear all

disp('AUTO-GENERATED CODE DESCRIPTION FOR CELL ANALYSIS');
disp('Jacob Kerssemakers 2017')


initval.do_singledir=0;  %Use this if you want to search one directory, no subdirectories

%paste directories and your search string (no *wildcards*)
initval.projectpath='D:\jkerssemakers\My Documents\BN CD Recent\BN_CD16_SandroFabai\Matlabcode\JacobsCode\';
initval.matlabsubpaths={''};   

switch 1
    case 1, initval.singledir=...  
    'D:\jkerssemakers\My Documents\BN CD Recent\BN_CD16_SandroFabai\Matlabcode\';
    case 2, initval.singledir=...  
    'D:\jkerssemakers\My Documents\BN CD Recent\BN_CD16_SandroFabai\Matlabcode\';
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%disp('start scan....');   
totalcodelines=0;
totalcharcount=0;
totalfunctioncount=0;
progdir=pwd;
lp=length(initval.matlabsubpaths);
foundmatches=0;
if initval.do_singledir, lp=1;end
for i=1:lp 
    p = genpath(char(strcat(initval.projectpath,initval.matlabsubpaths(i)))); 
    %String cotaining all (sub)dirs
    lp=length(p);
    cnt=0;
    oldi=1; nwi=oldi;
    while cnt<lp                        %separate out directory names
        cnt=cnt+1;
        nwi=nwi+1;
        str=char(p(cnt));
        if strcmp(str,';')              %This is one directory name
            dirnm=p(oldi:nwi-2);
            if initval.do_singledir, 
            dirnm=initval.singledir;
            cnt=lp;
            end
            dirnm;
            cd(dirnm);                       %read the m.file names in this directory
            FilNames=dir('*.m');
            lm=length(FilNames);
            for j=1:lm 
                nm=FilNames(j).name;
                xx=strfind(nm, '._');
                if length(xx)<1
                    filecontent=textread(nm, '%s', 'delimiter', '\n','whitespace', '');                   
                    mfilestruct=Evaluate_m_File(filecontent);
                    totalcodelines=totalcodelines+mfilestruct.mfilelength;
                    totalcharcount=totalcharcount+mfilestruct.charactercount;
                    totalfunctioncount=totalfunctioncount+mfilestruct.functioncount;
                    foundmatches=foundmatches+mfilestruct.tagline_number;
                    Evaluate_functions_in_mfile(filecontent,mfilestruct);
                end
            end
            oldi=nwi;
            cd(progdir);
        end     
    end
end
disp('number of matches');
disp(foundmatches);
disp('Matlab code associated with project:')
disp(initval.projectpath);
disp('number of functions scanned:');
disp(totalfunctioncount);
disp('number of code lines scanned:');
disp(totalcodelines);
disp('number of characters scanned:');
disp(totalcharcount);



function mfilestruct=Evaluate_m_File(content)
%This function evaluates a piece of matlab code 'content' for
%matlab functions, comments etc. It is intended to allow the user to see if
%functions are of interest to store separately.
   
    mfilestruct.tagline_number=0;        %number of taglines found
    mfilestruct.tagline_start=[];        %sets start line nrs. of sections enclosed by taglines
    mfilestruct.tagline_end=[];          %sets end line nrs. of sections enclosed by taglines
    lc=length(content);
    mfilestruct.mfilelength=lc;
    mfilestruct.charactercount=0;
    mfilestruct.functioncount=0;
    for k=1:lc  %read in all lines
        lne=(char(content(k)));  %this is the current line 
        mfilestruct.charactercount=mfilestruct.charactercount+length(lne);
        instructstart=strfind(lne, 'Use this section for a Quicksheet'); %dont list
        instructstop=strfind(lne,  'End of Quicksheet section'); %dont list
        instructskip=strfind(lne,'dont list');
        foundfunction=strfind(lne,'function');
        commentline=strfind(lne,'%');
        if length(foundfunction)>0 & isempty(commentline)
            mfilestruct.functioncount=mfilestruct.functioncount+1;
        end
        if length(instructstart)>0 & isempty(instructskip)  %found the sentence   
                mfilestruct.tagline_number=mfilestruct.tagline_number+1;
                mfilestruct.tagline_start=[mfilestruct.tagline_start k]; 
        end  
        if length(instructstop)>0  %found the sentence             
            %mfilestruct.tagline_number=mfilestruct.taglinenumber+1;
            mfilestruct.tagline_end=[mfilestruct.tagline_end k]; 
        end  
    end
    mfilestruct.tagline_start=[mfilestruct.tagline_start lc];
    mfilestruct.tagline_end=[mfilestruct.tagline_end lc];
   
    
    
function Evaluate_functions_in_mfile(filecontent,mfilestruct);
%This functiom takes function-headered sections of code out of a file; the
%user can decide to watch it and to judge its uefullness. JacobKers2014

%mfilestruct.functionnumber       %number of functions found
%mfilestruct.functionheaderlines  %line indices, including the last line

flines=mfilestruct.tagline_start;
flines_end=mfilestruct.tagline_end;
f=flines(end);

for i=1:length(flines)-1;
     msg1=strcat('Section in:',...
                char(filecontent(1)),...
                ' starting at line: ',...
                num2str(flines(i)),...
                ' '); 
    disp(msg1);

    for k=flines(i)+1:flines_end(i)-1  %Display the instruction lines
      msg3=char(filecontent(k));
      disp(msg3);
    end
    disp(' ');
end           
