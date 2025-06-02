
""" 
This B30 loads results from B20 and the traces plus kymographs. 
It co-plots these and allows the user to click specific points of interest
next, these clicked positions are refined, for example to find a step, or a peak.

# theme: B30_timings
# for hemi&full fusion: appearance times & main peak & second peak times
results should be saved per theme. data is added, but all the former acquired data (B20) is co-saved
"""
import json
import tkinter as tk
from skimage import io
import numpy as np
import pandas as pd
import csv
import math as mt
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from scipy.optimize import curve_fit
from common_tools import guv_tools
from scipy.stats import linregress
from itertools import combinations


def collect_them(exps):
    for initval in exps:
        label=initval.unique_label
        moviepath=initval.moviepath
        savepath=initval.savepath
        movie_filename = initval.movie_filename
        filename =initval.spot_image    
        xls_classification = initval.savepath / initval.xls_classification_file
        csv_source=initval.savepath /  str('B20_peak_analysis_' + label +'/' + 'B20_event_times.csv')
        
        in_path = initval.savepath / str('B30_user_classification_' + label +'/')
        xls_target=in_path / 'B30_event_times.xlsx'
        pix2um=0.1254
        frame_to_ms=50
        

        # Read the existing csv file with data
        events_df =pd.read_csv(csv_source,delimiter=';')

        # Add new columns with data
        man_appear=[]
        man_peak1=[]
        man_peak2=[]
        man_disappear=[]
        man_centersum=[]
        man_vesiclesum=[]
        man_residusum=[]
        man_type=[]

        for ix, umbra in enumerate(events_df['t0']):
            event_index=events_df.iloc[ix]["event"]
            print("B30_event:" + str(ix))
            t0=int(events_df.iloc[ix]["t0"])

            #check here if this event was user_ clicked (then a json exists)
            json_name='event' + str(int(event_index)).zfill(4) + '_clicks.json'
            full_path = in_path / json_name

            if full_path.exists():
                print(json_name + ':exists')
                event_df = pd.read_json(str(full_path))
                event_df.replace(-10E6, np.nan, inplace=True)
                event_df.replace(-20E6, np.nan, inplace=True)


                man_appear.append(event_df["t_appear_ms"][0])
                man_peak1.append(event_df["t_pk1_ms"][0])
                man_peak2.append(event_df["t_pk2_ms"][0])
                man_disappear.append(event_df["t_disapp_ms"][0])
                man_centersum.append(event_df["I_tpeak_center_ring"][0])
                man_vesiclesum.append(event_df["I_tpeak_allrings"][0])
                man_residusum.append(event_df["residusum"][0])
                man_type.append(event_df["type"][0])
            else:  #not measured
                man_appear.append(float("nan"))
                man_peak1.append(float("nan"))
                man_peak2.append(float("nan"))
                man_disappear.append(float("nan"))
                man_centersum.append(-2)
                man_vesiclesum.append(-2)
                man_residusum.append(-2)
                man_type.append('n/a')
       
        events_df['user_appearance(rel. to rise)'] = man_appear  # Example values
        events_df['user_man_peak1(rel. to rise)'] = man_peak1 # Example values
        events_df['user_man_peak2(rel. to rise)'] = man_peak2 # Example values
        events_df['user_disappear'] = man_disappear # Example values
        events_df['user_man_centerpeaksum'] = man_centersum # Example values
        events_df['user_man_vesiclepeaksum'] = man_vesiclesum # Example values
        events_df['user_man_residusum'] = man_residusum # Example values
        events_df['user_type'] = man_type # Example values

        # Display the updated data
        #print("\nUpdated Data with New Columns:")
        #print(events_df)

        # Write the updated data to a new Excel file
        events_df.to_excel(xls_target, index=False)

        print(f"\nUpdated data has been written to target")
