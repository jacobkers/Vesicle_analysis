# -*- coding: utf-8 -*-
"""
2024
@author: jkerssemakers
configuration of fusion experiments.
experiment run indices 
"""

import numpy as np
from pathlib import Path

class Fusion_experiment:
    """
    sets paths, names
    """
    def __init__(self): 
        self.label='2_TIRF_488_001_PCPG_Chol_small_short'
        self.moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
        self.savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        self.movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short.tif'
        self.filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short.tif'
        self.xls_classification_file  =  "kymographs_2_TIRF_488_001_PCPG_Chol_long_events_classification_jacob.xlsx"  
        

# overview of experiments:
def get_exps(exp_idx):  
    all_fusion_exps=[]

    #set up various experiment configurations:    
    Exp0 = Fusion_experiment()   
    Exp0.label='2_TIRF_488_001_PCPG_Chol_small_short'
    Exp0.moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    Exp0.savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    Exp0.movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short.tif'
    Exp0.filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short.tif'
    Exp0.xls_classification_file  =  "kymographs_2_TIRF_488_001_PCPG_Chol_small_short_events_classification_jacob.xlsx"  
    Exp0.suffix='.tif'
    all_fusion_exps.append(Exp0)

    Exp1 = Fusion_experiment() 
    Exp1.label='2_TIRF_488_001_PCPG_Chol_long'
    Exp1.moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    Exp1.savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    Exp1.movie_filename = '2_TIRF_488_001_PCPG_Chol.tif'
    Exp1.filename ='STD_2_TIRF_488_001_PCPG_Chol.tif'
    Exp1.xls_classification_file  =  "kymographs_2_TIRF_488_001_PCPG_Chol_long_events_classification_jacob.xlsx"  
    Exp1.suffix=Exp1.movie_filename[-4:] #of movie
    all_fusion_exps.append(Exp1)

    Exp2 = Fusion_experiment() 
    Exp2.label='Bert_nd2_test'
    Exp2.moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2024_Bert')
    Exp2.savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2024_Bert')
    Exp2.movie_filename = '50dotap_001_c1.tif'
    #Exp2.movie_filename = '50dotap_001.nd2'
    Exp2.filename ='MAX_50dotap_001_c1.tif'
    Exp2.suffix=Exp2.movie_filename[-4:] #of movie
    Exp2.dyechannel=1
    all_fusion_exps.append(Exp2)


    all_fusion_exps

    Experiment = all_fusion_exps[exp_idx]

    return Experiment
