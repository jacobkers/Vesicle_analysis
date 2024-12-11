
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

def on_click(click_event, points, ax, cid, cids):
    if click_event.button == 1 and click_event.inaxes == ax:  # Left-click
        # Find the nearest data point
        xdata, ydata = ax.lines[0].get_data()
        #distances = np.hypot(xdata - click_event.xdata, ydata - click_event.ydata)
        distances = abs(xdata - click_event.xdata)
        index = np.argmin(distances)
        point = (xdata[index], ydata[index])
        points.append(point)
        print(f"Selected point: {point}")
        ax.plot(point[0], point[1], 'ro')  # Mark the selected point
        plt.draw()
    elif click_event.button == 3:  # Right-click
        print("Selection ended for this plot.")
        plt.disconnect(cid)
        cids.remove(cid)
        plt.close()

def select_points(plots_data):
    all_selected_points = []

    for data in plots_data:
        fig, ax = plt.subplots()
        ax.plot(data[0], data[1], label='Data')
        ax.legend()
        plt.title("Left-click to select points, Right-click to erase last, y<0 to finish")

        selected_points = []
        cids = []
        cid = fig.canvas.mpl_connect('button_press_event', 
                                     lambda event: on_click(event, selected_points, ax, cid, cids))
        cids.append(cid)
        plt.show()

        all_selected_points.append(selected_points)

    return all_selected_points

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
    
    theme="double_release_timings"
    """  them, only two-peak events are considered.
    User clicks appearance, peak 1, peak 2
    """


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
    filtered_df = df[df['umbrella count'] == 2]

    # Display the filtered data
    #print("\nFiltered Data (length == 1):")
    #print(filtered_df)

    # Add new columns with data
    man_appear=[]
    man_rise=[]
    man_peak1=[]
    man_peak2=[]
    for ix, umbra in enumerate(filtered_df['umbrella count']):
        event_index=filtered_df.iloc[ix]["event"]
        t0=filtered_df.iloc[ix]["t0"]
        print("B30_event:" + str(ix))
        t0=filtered_df.iloc[ix]["t0"]
        #collect ring traces of this event
    
        trace_data_name='kymographs_' + label +'/csv/' + 'event' + str(event_index).zfill(4) +  str("_ring_traces_intensity.csv")
        csv_ring_traces=data_source_path /  trace_data_name
        ring_traces = np.loadtxt(csv_ring_traces, delimiter=';')
        
        # collect the kymograph
        kymo1_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_index).zfill(4) +  str("_XT_full.tif")
        kymo=io.imread(data_source_path / f"{kymo1_name}")
        if 1: #event_index == 209:
            sumtrace=np.sum(ring_traces, axis=1)
            centertrace=ring_traces[:,0]
            rr,cc=np.shape(kymo)
            plot_ring_traces = 0.9*cc-ring_traces/np.max(ring_traces)*0.8*cc
            fig, ax=plt.subplots(2,1)
            
            ax[0].imshow(np.log10(kymo.T),aspect='auto')
            ax[0].plot(plot_ring_traces)
            ax[0].plot(0*sumtrace+cc/2, 'w--')
            ax[0].plot(t0, plot_ring_traces[t0,0],'ro')
            ax[0].autoscale(enable=True, axis='x', tight=True)
            ax[1].plot(sumtrace)
            ax[1].plot(t0, sumtrace[t0],'ro')
            ax[1].legend(["sum"])
            ax[1].set_xlabel("frame no.")
            ax[1].set_ylabel("intensity, a.u.")
            ax[1].set_title('event:'+ str(event_index))
            fig.show()
            #let the user click:
            if theme =="double_release_timings":
                """  only two-peak events are considered.
                User clicks appearance, rise, peak 1, peak 2
                """
                axz=np.arange(len(centertrace))
                clickdata=[(axz,centertrace)]
                selpo=select_points(clickdata)
                selpo=selpo[0][-4:]  #last four points: appear, rise, peak1, peak2!
                t_appear_pix=selpo[0][0]
                t_rise_pix=selpo[1][0]
                t_pk1_pix=selpo[2][0]
                t_pk2_pix=selpo[3][0]
                
                #subpixel steps for peaks:
                spx1=guv_tools.subpix_step(centertrace[t_pk1_pix-1:t_pk1_pix+2])
                t_pk1_spx=t_pk1_pix+spx1
                spx2=guv_tools.subpix_step(centertrace[t_pk2_pix-1:t_pk2_pix+2])
                t_pk2_spx=t_pk2_pix+spx2

                #absolute, pixels
                t_appear_ms=(t_appear_pix-t_rise_pix)*frame_to_ms     #relative
                t_pk1_ms=(t_pk1_spx-t_rise_pix)*frame_to_ms         #relative
                t_pk2_ms=(t_pk2_spx-t_rise_pix)*frame_to_ms         #relative
                #allocate:
                man_rise.append(t_rise_pix)                 #absolute pixels
                man_appear.append(t_appear_ms)
                man_peak1.append(t_pk1_ms)
                man_peak2.append(t_pk2_ms)
                
            plt.close('all')
        else:
            man_appear.append(-1)
            man_rise.append(-1)
            man_peak1.append(-1)
            man_peak2.append(-1)
    filtered_df['man_t)_rise'] = man_rise # Example values
    filtered_df['man_appearance(rel. to rise)'] = man_appear  # Example values
    filtered_df['man_peak1(rel. to rise)'] = man_peak1 # Example values
    filtered_df['man_peak2(rel. to rise)'] = man_peak2 # Example values

    # Display the updated data
    #print("\nUpdated Data with New Columns:")
    #print(filtered_df)

    # Write the updated data to a new Excel file
    filtered_df.to_excel(xls_target, index=False)

    print(f"\nUpdated data has been written to target")
