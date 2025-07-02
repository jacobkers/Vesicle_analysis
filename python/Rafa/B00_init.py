# -*- coding: utf-8 -*-
"""
2024
@author: jkerssemakers
configuration of fusion experiments.
experiment run indices 
"""
import pandas as pd
import numpy as np
from pathlib import Path


class Fusion_experiment:
    """
    sets paths, names
    """
    def __init__(self): 
        self.label=''
        self.moviepath=Path('')
        self.savepath=Path('')
        self.movie_filename = ''
        self.filename =''
        self.xls_classification_file  =  ""  
        

# overview of experiments; each entry is a single movie
def get_exps():  
    overviewfile_path=Path("M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/membrane fusion")
    overviewfile_name =str("fusion_data_overview.xlsx")

    # Read as DataFrame:
    #uniqie_index unique_label	notes	exp_id	movie_id	sub_movie_id		use_it	
    #pathname	(sub)moviename	spot_image	event_classification

    df = pd.read_excel(overviewfile_path  / overviewfile_name)
    all_fusion_exps=[]
    df_to_use=df[df['use_it'] == 1]
    for ix, guvrow in enumerate(df_to_use["unique_index"]):
        movie_entry = Fusion_experiment()  
        movie_entry.global_index=df_to_use.iloc[ix]["unique_index"]
        movie_entry.unique_label=df_to_use.iloc[ix]["unique_label"]
        movie_entry.notes = df_to_use.iloc[ix]["notes"]
        movie_entry.exp_id = df_to_use.iloc[ix]["exp_id"]
        movie_entry.movie_id = df_to_use.iloc[ix]["movie_id"]
        movie_entry.sub_movie_id = df_to_use.iloc[ix]["sub_movie_id"]
        movie_entry.use_it=df_to_use.iloc[ix]["use_it"]
        movie_entry.moviepath=df_to_use.iloc[ix]["pathname"]      
        movie_entry.moviename = df_to_use.iloc[ix]["(sub)moviename"]
        movie_entry.spot_image = df_to_use.iloc[ix]["spot_image"]
        movie_entry.pix2um = df_to_use.iloc[ix]["pix2um"] 
        movie_entry.frame2ms = df_to_use.iloc[ix]["frame2ms"]
        movie_entry.zoom_lo = df_to_use.iloc[ix]["zoom_lo_frs"]
        movie_entry.zoom_hi = df_to_use.iloc[ix]["zoom_hi_frs"]
        movie_entry.trace_smooth = df_to_use.iloc[ix]["smoothwindow_frs"]
        movie_entry.suffix=movie_entry.moviename[-4:] #of movie
        print(movie_entry.global_index)
        all_fusion_exps.append(movie_entry)
        #extra:
        savepathname='M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/membrane fusion/' + movie_entry.unique_label
        movie_entry.savepath=Path(savepathname)

        #define a zoomed, and a full kymograph:
        movie_entry.rws=[0,1]
        movie_entry.DT_list=[200, 20000]  #duration
        movie_entry.pre_shift_list=[30,200000] #frames before start

    return all_fusion_exps
