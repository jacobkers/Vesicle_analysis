
""" 
This B30 loads results from B20 and the traces plus kymographs. 
It co-plots these and allows the user to click specific points of interest
next, these clicked positions are refined, for example to find a step, or a peak.

# theme: B30_timings
# for hemi&full fusion: appearance times & main peak & second peak times
results should be saved per theme. data is added, but all the former acquired data (B20) is co-saved
"""


from skimage import io
import numpy as np
import csv
import math as mt
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from scipy.optimize import curve_fit
from common_tools import guv_tools
from scipy.stats import linregress
from itertools import combinations

class Event:
    def __init__(self):
        self.index = 0
        self.x0 = 0
        self.y0 = 0
        self.t0 = 0
        self.type = 0

def find_peak_from(trace,t_start, direction, max_or_min):
    #find first maximum or minimum before or after
    #we start at the steepest rise
    #back or forward in time we find the last time-above_background
    #in both cases, times may be at be at the begin- or end-of-movie
    t_scan=t_start
    t_ext=t_start
    stopit=False
    while t_scan>1 and t_scan<len(trace)-2 and stopit == False:
        t_scan=t_scan+direction
        local_extremum=(max_or_min*trace[t_scan]>max_or_min*trace[t_scan+direction] and 
                        max_or_min*trace[t_scan]>max_or_min*trace[t_scan-direction])
        if local_extremum:
            t_ext=t_scan
            stopit=True
        else:
            stopit=False
   
    return t_ext

def travel_from_start(pre_trace, t_rise, bck, direction):
    #this function analyzes a single event in more detail
    #we start at the steepest rise
    #back or forward in time we find the last time-above_background
    #in both cases, times may be at be at the begin- or end-of-movie
       
    t_border=t_rise
    t_scan=t_rise
    stopit=False
    while t_scan>0 and t_scan<len(pre_trace)-1 and stopit == False:
        t_scan=t_scan+direction
        if pre_trace[t_scan]>bck:
            t_border=t_scan
        else:
            stopit=True
   
    return t_border

import numpy as np
import pandas as pd

def fusion(modus):
    # Example usage
    if modus == 'short':
        label='2_TIRF_488_001_PCPG_Chol_small_short'
        data_source_path=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        xls_source  = data_source_path / "kymographs_2_TIRF_488_001_PCPG_Chol_small_short/B20_event_times_edits.xlsx" 
        xls_target  = data_source_path / "kymographs_2_TIRF_488_001_PCPG_Chol_small_short/B30_TEST.xlsx"  
    else:
        label='2_TIRF_488_001_PCPG_Chol_long'
        data_source_path=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        xls_source  = data_source_path / "kymographs_2_TIRF_488_001_PCPG_Chol_long/B20_event_times_edits.xlsx" 
        xls_target  = data_source_path / "kymographs_2_TIRF_488_001_PCPG_Chol_long/B30_TEST.xlsx"  
    pix2um=0.1254
    frame_to_ms=50
    

    #load pre-traces
    trace_data_name=label +"_traces" +  str(".csv")
    csv_traces=data_source_path /  trace_data_name
    csv_path_in = Path(csv_traces)
    print(csv_traces.stem)
    pre_trace_data = np.loadtxt(csv_traces, delimiter=';')


    # Read the existing Excel file
    xls_source = data_source_path / xls_source
    df = pd.read_excel(xls_source)

    # Display the data read from the Excel file
    #print("Original Data:")
    #print(df)


    # Apply a filter to include only rows where the 'length' column equals 1
    filtered_df = df[df['umbrella count'] >= 1]

    # Display the filtered data
    #print("\nFiltered Data (length == 1):")
    #print(filtered_df)

    # Add new columns with data
    man_appear=[]
    new_data2=[]
    for ix, umbra in enumerate(filtered_df['umbrella count']):
        event_index=filtered_df.iloc[ix]["event"]
        print("B30_event:" + str(ix))
        t0=filtered_df.iloc[ix]["t0"]
        #collect ring traces of this event
    
        trace_data_name='kymographs_' + label +'/csv/' + 'event' + str(event_index).zfill(4) +  str("_ring_traces_intensity.csv")
        csv_ring_traces=data_source_path /  trace_data_name
        ring_traces = np.loadtxt(csv_ring_traces, delimiter=';')
        
        # and the kymograph
        kymo1_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_index).zfill(4) +  str("_XT_full.tif")
        kymo=io.imread(data_source_path / f"{kymo1_name}")
        if 0:
            rr,cc=np.shape(kymo)
            plot_ring_traces = 0.9*cc-ring_traces/np.max(ring_traces)*0.8*cc
            fig, ax=plt.subplots(2,1)
            ax[0].imshow(np.log10(kymo.T),aspect='auto')
            ax[0].plot(plot_ring_traces)
            ax[0].plot(t0, plot_ring_traces[t0,0],'ro')
            ax[0].autoscale(enable=True, axis='x', tight=True)
            ax[1].plot(np.sum(ring_traces, axis=1))
            ax[1].legend(["sum"])
            ax[1].set_xlabel("frame no.")
            ax[1].set_ylabel("intnesity, a.u.")
            fig.show()
            dum=1
            plt.close('all')
        if umbra>1:
            pick_time=umbra
            man_appear.append(pick_time)
            new_data2.append(5)
        else:
            man_appear.append(1)
            new_data2.append(10)
    filtered_df['man_appearance 1'] = man_appear  # Example values
    filtered_df['New Column 2'] = new_data2 # Example values

    # Display the updated data
    #print("\nUpdated Data with New Columns:")
    #print(filtered_df)

    # Write the updated data to a new Excel file
    output_file = "output.xlsx"  # Replace with your desired output file path
    filtered_df.to_excel(xls_target, index=False)

    print(f"\nUpdated data has been written to {output_file}")
