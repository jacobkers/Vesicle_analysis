function init=A000_get_config(expno)
%common:
close all;
codepth=pwd;
addpath(genpath('tools'));
cd .., addpath(genpath('common_tools')), cd(codepth);

init.look_ahead=1;
init.skips=10;
%specific:
switch expno
    case 1
        %% Notes
        %Blue: fusion channel
        %Green: reference GUV channel
        %Red: permeabilization channel
        %% Settings
        %IN paths & names:
        init.main_path=swap_path('M:\tnw\bn\cd\Shared\Rafael Lira\Test Jacob\');
        init.exp_path=[init.main_path, '2023_11_27 Test02_30 uM LUVs_WITHCerC6\'];        
        %this should match the saved name exactly:
        init.muscope_exportname='30 uM LUVs_WITHCerC6 real time_Series011_t00_overlay';
        %...combined with above, this sets what tiffs to look for per channel:
        init.chan_suffixes=[{'.tif (blue)'},{'.tif (green)'},{'.tif (red)'}];
        %set what channel is used for object detection:
        init.chan_ref_id=2;
        %name of file that contains selected rois (ImageJ)
        init.filename_rois='ROIS.csv';
        %OUT paths & names:
        mainsavepath=swap_path('M:\tnw\bn\cd\Shared\Jacob\TESTdata_out\Rafa\');
        init.savename='30 uM LUVs_WITHCerC6 real time_Series011_t00';
        init.savepath=[mainsavepath init.savename, '\'];

    case 0 
        %% Notes: 
        %pilot, 3 ROIs
        %% Settings
        %IN paths & names:
        init.main_path=swap_path('CD_Data_in\2023_Rafa\');
        init.exp_path=[init.main_path, '2023_10_02 Test image analysis\'];
        init.savename='40 uM LUVsWITHCerC6_RealTime_Series002_t000';
        %this should match the saved name exactly:
        init.muscope_exportname='40 uM LUVsWITHCerC6_RealTime_Series002_t000_overlay';
        %...combined with above, this sets what tiffs to look for per channel:
        init.chan_suffixes=[{'.tif (green)'},{'.tif (red)'}];
        %set what channel is used for object detection:
        init.chan_ref_id=1;
        %name of file that contains selected rois (ImageJ)
        init.filename_rois='ROIS.csv';
        %OUT paths & names:
        mainsavepath=swap_path('M:\tnw\bn\cd\Shared\Jacob\TESTdata_out\Rafa\2023_10_02 Test image analysis\');
        init.savepath=[mainsavepath init.savename, '\'];
        

end
