
""" 
This B30 loads results from B20 and the traces plus kymographs. 
It co-plots these and allows the user to click specific points of interest
next, these clicked positions are refined, for example to find a step, or a peak.

# theme: B30_timings
# for hemi&full fusion: appearance times & main peak & second peak times
results should be saved per theme. data is added, but all the former acquired data (B20) is co-saved
"""

import numpy as np
import pandas as pd
import csv
import math as mt
from pathlib import Path
import matplotlib.pyplot as plt

fig, ax=plt.subplots(1,1)
legenda=[]
def collect_them(exps):
    for initval in exps:
        label=initval.unique_label

        in_path = initval.savepath / str('B30_user_classification_' + label +'/')
        xls_target=in_path / 'B30_event_times.xlsx'
        pix2um=initval.pix2um
        frame_to_ms=initval.frame2ms
        
        events_df=pd.read_excel(xls_target)
        print(events_df.columns)
        sub_events_df=events_df[events_df["user_type"]=="single_release"]
        print(sub_events_df.head())
        
        peakval=sub_events_df["I_center_peakval"]
        appear=sub_events_df["user_appearance(rel. to rise)"]
        release_1=sub_events_df["user_man_peak1(rel. to rise)"]
        delaytime=release_1-appear       
        
        legenda.append(label)
        ax.plot(peakval,delaytime,'o')
        ax.set_ylabel("delay, ms")
        ax.set_xlabel("peak intensity, a.u.")
        ax.legend(legenda)
        fig.show()
    dum=1

