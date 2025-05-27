
""" 
This B30 loads results from B20 and the traces plus kymographs. 
It co-plots these and allows the user to click specific points of interest
next, these clicked positions are refined, for example to find a step, or a peak.

# theme: B30_timings
# for hemi&full fusion: appearance times & main peak & second peak times
results should be saved per theme. data is added, but all the former acquired data (B20) is co-saved
"""

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

class Event:
    def __init__(self):
        self.index = 0
        self.x0 = 0
        self.y0 = 0
        self.t0 = 0
        self.type = 0

def on_click(fig,event, selected_points, ax, cid, cids):
    if event.button == 1:  # Right-click
        # Always use display (pixel) coordinates and convert to data
        display_coords = (event.x, event.y)
        inv = ax.transData.inverted()
        data_coords = inv.transform(display_coords)
        xdata, ydata = data_coords

        print(f"Estimated data coords (even outside axes): x={xdata:.2f}, y={ydata:.2f}")
        selected_points.append((xdata, ydata))

        # Mark point only if inside axes (for visibility)
        if event.inaxes:
            ax.plot(xdata, ydata, 'ro')
            fig.canvas.draw()
    elif event.button == 3:  # Right-click
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



def fusion(exps):
    # Get screen dimensions
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # DPI (dots per inch)
    dpi = 100  # default DPI for matplotlib

    # Calculate figure size in inches (0.8× screen size)
    fig_width = 0.8 * screen_width / dpi
    fig_height = 0.8 * screen_height / dpi

    for initval in exps:
        label=initval.unique_label
        moviepath=initval.moviepath
        savepath=initval.savepath
        movie_filename = initval.movie_filename
        filename =initval.spot_image    
        xls_classification = initval.savepath / initval.xls_classification_file
        csv_source=initval.savepath /  str('B20_peak_analysis_' + label +'/' + 'B20_event_times.csv')
        
        out_path = initval.savepath / str('B30_user_classification_' + label +'/')
        if not out_path.is_dir():
            out_path.mkdir()
        xls_target=out_path + 'B30_event_times.csv'
        pix2um=0.1254
        frame_to_ms=50
        
        

        



        #load pre-traces
        trace_data_name=str("B00_"+ label +"_traces" +  str(".csv"))
        csv_traces=initval.savepath  /   trace_data_name
        csv_path_in = Path(csv_traces)
        pre_trace_data = np.loadtxt(csv_traces, delimiter=';')


        # Read the existing csv file
        events_df =pd.read_csv(csv_source,delimiter=';')


        # Apply a filter to include only rows where the 'length' column equals 1

        # Display the filtered data
        #print("\nFiltered Data (length == 1):")
        #print(events_df)

        # Add new columns with data
        man_appear=[]
        man_peak1=[]
        man_peak2=[]
        man_disappear=[]
        man_vesiclesum=[]
        man_residusum=[]

        for ix, umbra in enumerate(events_df['t0']):
            event_index=events_df.iloc[ix]["event"]
            print("B30_event:" + str(ix))
            t0=int(events_df.iloc[ix]["t0"])
            #collect ring traces of this event
        
            trace_data_name='B10_kymographs_' + label +'/csv/' + 'event' + str(int(event_index)).zfill(4) +  str("_ring_traces_intensity.csv")
            csv_ring_traces=savepath /  trace_data_name
            ring_traces = np.loadtxt(csv_ring_traces, delimiter=';')
            
            # collect the kymograph
            kymo1_name = 'B10_kymographs_' + label +'/kymos/' + 'event' + str(int(event_index)).zfill(4) +  str("_XT_full.tif")
            kymo=io.imread(savepath / f"{kymo1_name}")
            if 1: #event_index == 209:
                
                sumtrace=np.sum(ring_traces, axis=1)
                centertrace=ring_traces[:,0]
                rr,cc=np.shape(kymo)
                plot_ring_traces = 0.9*cc-ring_traces/np.max(ring_traces)*0.8*cc
                #fig, ax=plt.subplots(1,1)
                fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
                ax.imshow(np.log10(kymo.T),aspect='auto')
                ax.plot(plot_ring_traces)
                ax.plot(0*sumtrace+cc/2, 'w--')
                ax.plot(t0, plot_ring_traces[t0,0],'ro')
                ax.autoscale(enable=True, axis='x', tight=True)
                ax.set_title('event:'+ str(event_index))
                ax.set_ylim([1.1*cc,0])
                """ ax[0].imshow(np.log10(kymo.T),aspect='auto')
                ax[0].plot(plot_ring_traces)
                ax[0].plot(0*sumtrace+cc/2, 'w--')
                ax[0].plot(t0, plot_ring_traces[t0,0],'ro')
                ax[0].autoscale(enable=True, axis='x', tight=True)
                ax[0].set_title('event:'+ str(event_index))
                ax[1].plot(sumtrace)
                ax[1].plot(t0, sumtrace[t0],'ro')
                ax[1].legend(["sum"])
                ax[1].set_xlabel("frame no.")
                ax[1].set_ylabel("intensity, a.u.")
                ax[1].set_title('event:'+ str(event_index)) """
                fig.show()
                
                #user clicks:
                #axz=np.arange(len(centertrace))
                #clickdata=[(axz,centertrace)]
                #selpo=select_points(clickdata)
                ax.set_title(str(int(event_index))+"Left:select, Right:next, <0: =nan")

                selected_points = []
                cids = []
                cid = fig.canvas.mpl_connect('button_press_event', 
                                            lambda event: on_click(fig,event, selected_points, ax, cid, cids))
                cids.append(cid)
                plt.show()

                selpo=selected_points

                #reject_checks:
                if selpo[0][1]<cc: 
                    t_appear_pix=int(selpo[0][0])     
                else: t_appear_pix=-1
                if selpo[1][1]<cc: 
                    t_pk1_pix=int(selpo[1][0])
                    spx1=guv_tools.subpix_step(centertrace[t_pk1_pix-1:t_pk1_pix+2])
                    t_pk1_spx=t_pk1_pix+spx1 
                else: 
                    t_pk1_pix=-1
                    t_pk1_spx=-1
                if selpo[2][1]<cc: 
                    t_pk2_pix=int(selpo[2][0])
                    spx2=guv_tools.subpix_step(centertrace[t_pk2_pix-1:t_pk2_pix+2])
                    t_pk2_spx=t_pk2_pix+spx2
                else: 
                    t_pk2_pix=-1
                    t_pk2_spx=-1

                if selpo[3][1]<cc: 
                    t_disapp_pix=int(selpo[3][0])
                else: t_disapp_pix=-1
                

                #absolute, pixels
                t_appear_ms=(t_appear_pix-t0)*frame_to_ms     #relative
                t_pk1_ms=(t_pk1_spx-t0)*frame_to_ms         #relative
                t_pk2_ms=(t_pk2_spx-t0)*frame_to_ms         #relative
                t_disapp_ms=(t_disapp_pix)*frame_to_ms
                if t_pk1_pix>0:
                    residutime=50 #in frames
                    residu_time=min([len(sumtrace), t_pk1_pix+residutime])
                    vesiclesum=sumtrace[t_pk1_pix]
                    residusum=sumtrace[residu_time]
                else:
                    vesiclesum=-1
                    residusum=-1

                #allocate:
                
                man_appear.append(t_appear_ms)
                man_peak1.append(t_pk1_ms)
                man_peak2.append(t_pk2_ms)
                man_disappear.append(t_disapp_ms)      
                man_vesiclesum.append(vesiclesum)
                man_residusum.append(residusum)
     
                plt.close('all')
            else:
                man_appear.append(-1)
                man_peak1.append(-1)
                man_peak2.append(-1)
                man_disappear.append(-1)
                man_vesiclesum.append(-1)
                man_residusum.append(-1)

        
        events_df['man_appearance(rel. to rise)'] = man_appear  # Example values
        events_df['man_peak1(rel. to rise)'] = man_peak1 # Example values
        events_df['man_peak2(rel. to rise)'] = man_peak2 # Example values
        events_df['disappear'] = man_disappear # Example values
        events_df['man_vesiclepeaksum'] = man_vesiclesum # Example values
        events_df['man_residusum'] = man_residusum # Example values

        # Display the updated data
        #print("\nUpdated Data with New Columns:")
        #print(events_df)

        # Write the updated data to a new Excel file
        events_df.to_excel(xls_target, index=False)

        print(f"\nUpdated data has been written to target")
