function initval=A000__WF_Get_FF_PathsandExperiments(batchrunindex);
%See below code for explanation


%% Paths
if ismac, initval.DirSep='/';else initval.DirSep='\';end;
initval.codepth='D:\jkerssemakers\My Documents\BN CD Recent\BN_CD16_Fede\Matlabcode_Fedalyzer\';

initval.projectpath='D:\jkerssemakers\My Documents\BN CD Data\2016_Fede\'; 
%initval.codepth=pwd;
addpath(initval.codepth);
addpath(strcat(initval.codepth,initval.DirSep,'CommonTools',initval.DirSep));


%% Experiment labels
switch batchrunindex
    case 1, initval.expi='VersionTest'  %local Jacob
    case 2, initval.expi='17-08-16 12uM FtsZ';   
end

%common props
initval.dummy=1;
%% General Alignment settings. For effecting these, re-run A020 and higher 


%% experiment-specific settings
switch initval.expi
    case 'VersionTest'    %TEST Data
        initval.datasourcepath=char(strcat(initval.projectpath,'FF_TESTdata',initval.DirSep));   
    case '17-08-16 12uM FtsZ'   %test Data on K
        initval.datasourcepath='K:\bn\cd\Shared\Federico\Jacob\17-08-16 12uM FtsZ\';   
end
initval.resultpath=strcat(initval.projectpath,'BatchanalysisResults',initval.DirSep,...
                            'Results_',initval.expi,initval.DirSep);

%% get deailed info for experiment
[numdat,textdat]= xlsread(strcat(initval.codepth,initval.DirSep,'FF_ExperimentOverview.xlsx'));

 Headers=textdat(1,:);
 col_Exps=find(strcmp(Headers,'ExpLabel')); %identify type column
 Exps=textdat(2:end,col_Exps);
 Exp_Row=find(strcmp(Exps,initval.expi)); 
 initval.dummynumber=numdat(Exp_Row,(find(strcmp(Headers,'dummynumberparameter')))-1);
 initval.dummytext=char(textdat(Exp_Row+1,(find(strcmp(Headers,'dummytextparameter')))));
 

% 'Use this section for a Quicksheet'
%-----------------------------------------------------------------                                
     %---------------------------------------------------------------------\     
% 'End of Quicksheet section'


