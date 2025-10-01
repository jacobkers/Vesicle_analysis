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
        self.short_set=-1
        if self.short_set>0:
            self.nc_name="_all_guvs_short.nc"
        else:
            self.nc_name = "_all_guvs.nc"

# overview of experiments:
def get_exps(exp_idx):
    #use 1st decimal to pick drive:
    exp_idx_base=int(np.round(exp_idx))
    exp_idx_dec=int(round(10*(exp_idx-np.round(exp_idx))) )
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
   
    Exp1 = Guv_experiment()
    Exp1.exp_id = 0
    Exp1.mainpath_in=in_root+ str("pilots/")
    Exp1.mainpath_out =out_root + str("pilots/")   
    Exp1.subdir = str("20082025_CS_test/")
    Exp1.movienames = ["tiff_00", "tiff_01"]  # the ones that have ROIs measured in ImageJ
    #Exp1.movienames = ["tiff_01"]  # the ones that have ROIs measured in ImageJ

    Exp1.suffix='.tif'
    Exp1.tracking_key=[0]  #write as list! #1: use hand-set drift #2: use x, y from prior run A20
    Exp1.N_colors=1
    Exp1.sequence='time_trace'
    Exp1.movie_id = -1 #if not -1, test only this movie_id
    all_Experiments = [Exp1]

    Experiment = all_Experiments[exp_idx_base]

    return Experiment
