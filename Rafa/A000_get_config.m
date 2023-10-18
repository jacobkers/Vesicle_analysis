function init=A000_get_config(expno)
%common:
close all;
codepth=pwd;
cd .., addpath(genpath('vesicle_tools')), cd(codepth);
init.main_path=swap_path('CD_Data_in\2023_Rafa\');
init.look_ahead=1;
%specific:
switch expno
    case 0        
        init.exp_path=[init.main_path, '2023_10_02 Test image analysis\'];
        init.savename='40 uM LUVsWITHCerC6_RealTime_Series002_t000';
        init.filename_green=[init.savename '_green.tif'];
        init.filename_red=[init.savename '_red.tif'];
        init.filename_rois=[init.savename '_ROIs.csv'];
        init.savepath=swap_path('Dropbox\CD_Data_out\2023_Rafael\2023_10_02 Test image analysis\');
end
