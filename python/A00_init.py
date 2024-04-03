# -*- coding: utf-8 -*-
"""
2024
@author: jkerssemakers
configuration of guv experiments.
experiment run indices (add 0.1 to run on K:):
0: .nd testfiles
1: .lif testfiles 
"""

import numpy as np

class Guv_experiment:
    """
    sets paths, names
    """
    def __init__(self):
        self.mainpath_in = str(
            "M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.mainpath_out = str(
            "M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.subdir = str()
        self.movienames = []
        self.suffix='.tif'
        self.tracking_key=0  #channel index to use for obtaining geometry

# overview of experiments:
def get_exps(exp_idx):
    #use 1st decimal to pick drive:
    exp_idx_base=int(np.round(exp_idx))
    exp_idx_dec=int(10*(exp_idx-np.round(exp_idx))) 
    if exp_idx_dec==0: #laptop
        in_root=str("C:/Users/jkerssemakers/CD_Data_in/2023_Rafa//")
        out_root=str("C:/Users/jkerssemakers/Dropbox/CD_Data_out/2023_Rafa/")
    if exp_idx_dec==1:
        in_root=str("D:/jkerssemakers/CD_Data_in/2023_Rafa/")
        out_root=str("D:/jkerssemakers/CD_Data_out/2023_Rafa/")
    if exp_idx_dec==2: #remote
        in_root=str("M:/tnw/bn/cd/Shared/Jacob/TESTdata_in/2023_Rafa/")
        out_root=str("M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/2023_Rafa/")
    #set up various experiment configurations:    
    Exp0 = Guv_experiment()   
    Exp0.mainpath_in=in_root+ str("Test_subdir_nd/")
    Exp0.mainpath_out =out_root + str("Test_subdir_nd/")   
    Exp0.subdir = str("60 uM_1h incubation/")
    Exp0.movienames = ["1", "2", "3", "16", "9"]  # the ones that have ROIs measured in ImageJ
    Exp0.suffix='.nd2'
    

    Exp1 = Guv_experiment()
    Exp1.mainpath_in=in_root+ str("Test_subdir_lif/")
    Exp1.mainpath_out=out_root+ str("Test_subdir_lif/")
    Exp1.subdir = str("40mMLUVs_WITHCerC6/")
    Exp1.movienames = ["40mMLUVs_WITHCerC6"]  # the ones that have ROIs measured in ImageJ
    Exp1.suffix='.lif'

    Exp2 = Guv_experiment()
    Exp2.mainpath_in=in_root+ str("Test_subdir_tif/")
    Exp2.mainpath_out=out_root+ str("Test_subdir_tif/")
    Exp2.subdir = str("40 uM LUVsWITHCerC6/")
    Exp2.movienames = ["40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp"]  # the ones that have ROIs measured in ImageJ
    Exp2.suffix='.tif'

    Exp3 = Guv_experiment()
    Exp3.mainpath_in=in_root+ str("Test_subdir_tif/")
    Exp3.mainpath_out=out_root+ str("Test_subdir_tif/")
    Exp3.subdir = str("Less challenging GUV/")
    Exp3.movienames = ["30 uM LUVs_WITHCerC6 real time_Series011_t00_overlay"]  # the ones that have ROIs measured in ImageJ
    Exp3.suffix='.tif'
    Exp3.tracking_key=2

    all_Experiments = [Exp0, Exp1, Exp2, Exp3]

    Experiment = all_Experiments[exp_idx_base]

    return Experiment
