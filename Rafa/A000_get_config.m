function init=A000_get_config(expno)
%common:
close all;
codepth=pwd;
addpath(genpath('tools'));
cd .., addpath(genpath('common_tools')), cd(codepth);
init.main_path=swap_path('CD_Data_in\2023_Rafa\');
init.look_ahead=1;
%specific:
switch expno
    case -1
        init.exp_path=[init.main_path, 'typical dirname for an experiment\'];
        init.savename='the name to be used for output data';
        %following sets also reading format:
        init.filename_green=[init.savename '_green.tif'];
        init.filename_red=[init.savename '_red.tif'];
        init.filename_rois=[init.savename '_ROIs.csv'];
        init.savepath=swap_path('Dropbox\CD_Data_out\2023_Rafael\2023_10_02 Test image analysis\');
        mainsavepath=swap_path('M:\tnw\bn\cd\Shared\Jacob\TESTdata_out\Rafa\2023_10_02 Test image analysis\');
        init.savepath=[mainsavepath init.savename, '\'];
    case 0        
        init.exp_path=[init.main_path, '2023_10_02 Test image analysis\'];
        init.savename='40 uM LUVsWITHCerC6_RealTime_Series002_t000';
        init.muscope_exportname='40 uM LUVsWITHCerC6_RealTime_Series002_t000_overlay';
        init.chan_suffixes=[{'.tif (green)'},{'.tif (red)'}];
        init.chan_ref_id=1;
        init.savepath=swap_path('Dropbox\CD_Data_out\2023_Rafael\2023_10_02 Test image analysis\');
        mainsavepath=swap_path('M:\tnw\bn\cd\Shared\Jacob\TESTdata_out\Rafa\2023_10_02 Test image analysis\');
        init.savepath=[mainsavepath init.savename, '\'];
        init.filename_rois='ROIS_40 uM LUVsWITHCerC6_RealTime_Series002_t000.csv';
    case 1
        init.exp_path='M:\tnw\bn\cd\Shared\Rafael Lira\Test Jacob\'
end
