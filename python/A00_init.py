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
import pathlib
class Guv_experiment:
    """
    sets paths, names
    """
    def __init__(self):
        self.mainpath_in = str(
            "M:/tnw/bn/cd/Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.mainpath_out = str(
            "M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.subdir = str()
        self.movienames = []
        self.suffix='.tif'
        self.tracking_key=0  #channel index to use for obtaining geometry
        self.N_colors=3
        self.sequence='time_trace'
        self.apply_drift_correction=False
        self.pix2mu=0.4141253
        self.counts2perc=1/4000 #app., see callibration_curve_EP.xlsx

# overview of experiments:
def get_exps(exp_idx):
    #use 1st decimal to pick drive:
    exp_idx_base=int(np.round(exp_idx))
    exp_idx_dec=int(10*(exp_idx-np.round(exp_idx))) 
    if exp_idx_dec==0: #laptop
        in_root=str("C:/Users/jkerssemakers/OneDrive - Delft University of Technology/CD_Data_in/2025_Charu//")
        out_root=str("C:/Users/jkerssemakers/OneDrive - Delft University of Technology/CD_Data_out/2025_Charu/")
    if exp_idx_dec==1:
        in_root=str("C:/Users/jkerssemakers/OneDrive - Delft University of Technology/CD_Data_in/2025_Charu//")
        out_root=str("C:/Users/jkerssemakers/OneDrive - Delft University of Technology/CD_Data_out/2025_Charu/")
    if exp_idx_dec==2: #remote
        in_root=str("M:/tnw/bn/cd/Shared/Jacob/TESTdata_in/2025_Charu/")
        out_root=str("M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/2025_Charu/")
    #set up various experiment configurations:    
    Exp0 = Guv_experiment()   
    Exp0.mainpath_in=in_root+ str("pilots/")
    Exp0.mainpath_out =out_root + str("pilots/")   
    Exp0.subdir = str("20082025_CS_test/")
    Exp0.movienames = ["20082025_CS_For Jacob.lif - R 4 - C=1"]  # the ones that have ROIs measured in ImageJ
    Exp0.suffix='.tif'
    Exp0.tracking_key=[0]  #write as list!
    Exp0.N_colors=1
    Exp0.sequence='time_trace'

    #1: use hand-set drift
    #2: use x, y from prior run A20

    
    all_Experiments = [Exp0]

    Experiment = all_Experiments[exp_idx_base]

    return Experiment
