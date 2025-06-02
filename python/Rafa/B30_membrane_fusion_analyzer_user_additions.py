
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

class Event:
    def __init__(self):
        self.index = 0
        self.x0 = 0
        self.y0 = 0
        self.t0 = 0
        self.type = 0

def on_click(fig,event, selected_points, ax, cid, cids):
    if event.button == 1:  # left-click
        # Always use display (pixel) coordinates and convert to data
        display_coords = (event.x, event.y)
        inv = ax.transData.inverted()
        data_coords = inv.transform(display_coords)
        xdata, ydata = data_coords

        #print(f"Estimated data coords (even outside axes): x={xdata:.2f}, y={ydata:.2f}")
        selected_points.append((xdata, ydata))

        # Mark point only if inside axes (for visibility)
        if event.inaxes:
            ax.plot(xdata, ydata, 'ro')
            fig.canvas.draw()
    if len(selected_points)==4:
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



def click_them(exps):
    # Get screen dimensions
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # DPI (dots per inch)
    dpi = 100  # default DPI for matplotlib

    # Calculate figure size in inches (0.8× screen size)
    fig_width = 0.8 * screen_width / dpi
    fig_height = 0.5 * screen_height / dpi

    

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
        frame_to_ms=initval.frame2ms       

        

        zoomsection=[-int(2000/initval.frame2ms),int(6000/initval.frame2ms)]  #for clicking, in frames (50 ms)


        #load pre-traces
        trace_data_name=str("B00_"+ label +"_traces" +  str(".csv"))
        csv_traces=initval.savepath  /   trace_data_name

        # Read the existing csv file
        events_df =pd.read_csv(csv_source,delimiter=';')

        # Display the filtered data
        #print("\nFiltered Data (length == 1):")
        #print(events_df)

        for ix, umbra in enumerate(events_df['t0']):
            event_index=events_df.iloc[ix]["event"]
            print("B30_event:" + str(ix))
            t0=int(events_df.iloc[ix]["t0"])

            #check here if this event was already clicked (then a json exists)
            json_name='event' + str(int(event_index)).zfill(4) + '_clicks.json'
            full_path = out_path / json_name

            if full_path.exists():
                print(json_name + ':exists')
            else:
                #collect ring traces of this event           
                trace_data_name='B10_kymographs_' + label +'/csv/' + 'event' + str(int(event_index)).zfill(4) +  str("_ring_traces_intensity.csv")
                csv_ring_traces=savepath /  trace_data_name
                ring_traces = np.loadtxt(csv_ring_traces, delimiter=';')
                
                # collect the kymograph
                kymo1_name = 'B10_kymographs_' + label +'/kymos/' + 'event' + str(int(event_index)).zfill(4) +  str("_XT_full.tif")
                kymo=io.imread(savepath / f"{kymo1_name}")
                sumtrace=np.sum(ring_traces, axis=1)
                centertrace=ring_traces[:,0]
                rr,cc=np.shape(kymo)

                plot_ring_traces = 0.9*cc-ring_traces/np.max(ring_traces)*0.8*cc
                #fig, ax=plt.subplots(1,1)
                fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
                ax.imshow(np.log10(kymo.T),aspect='auto')
                ax.plot(plot_ring_traces)
                ax.plot(plot_ring_traces[:,0], 'w-')
                ax.plot(0*sumtrace+cc/2, 'w--')
                ax.plot(t0, plot_ring_traces[t0,0],'ro')
                ax.autoscale(enable=True, axis='x', tight=True)
                ax.set_title('event:'+ str(event_index))
                ax.set_ylim([1.1*cc,-0.1*cc])
                ax.set_xlim([zoomsection[0]+t0,zoomsection[1]+t0])
                ax.set_title(str(int(event_index))+"Left:select, Right:next, <0: =nan")
                fig.show()

                selpo = []
                cids = []
                cid = fig.canvas.mpl_connect('button_press_event', 
                                            lambda event: on_click(fig,event, selpo, ax, cid, cids))
                cids.append(cid)
                plt.show()

                t0=float(t0)

                #reject_checks:
                if selpo[0][1]<cc: 
                    t_appear_pix=int(selpo[0][0]) 
                    t_appear_ms=(t_appear_pix-t0)*frame_to_ms      
                else: 
                    t_appear_pix=-10E6
                    t_appear_ms=-10E6
                if selpo[1][1]<cc: #good one, refine
                    t_clicked=int(selpo[1][0])
                    t_pk1_pix = t_clicked + np.argmax(centertrace[max(t_clicked-3,0):t_clicked+4])
                    spx1=guv_tools.subpix_step(centertrace[t_pk1_pix-1:t_pk1_pix+2])
                    t_pk1_spx=t_pk1_pix+spx1 
                    t_pk1_ms=(t_pk1_spx-t0)*frame_to_ms      
                else: 
                    t_pk1_pix=-10E6
                    t_pk1_spx=-10E6
                    t_pk1_ms=-10E6
                if selpo[2][1]<cc and selpo[2][1]>0:  #second release, refine
                    t_clicked=int(selpo[2][0])
                    t_pk2_pix= t_clicked + np.argmax(centertrace[max(t_clicked-3,0):t_clicked+4])
                    spx2=guv_tools.subpix_step(centertrace[t_pk2_pix-1:t_pk2_pix+2])
                    t_pk2_spx=t_pk2_pix+spx2
                    t_pk2_ms=(t_pk2_spx-t0)*frame_to_ms 
                if selpo[2][1]>cc:  #no second release
                    t_pk2_pix=-10E6
                    t_pk2_spx=-10E6
                    t_pk2_ms=-10E6      
                if selpo[2][1]<0:  #multiple/other
                    t_pk2_pix=-20E6
                    t_pk2_spx=-20E6
                    t_pk2_ms=-20E6
                if selpo[3][1]<cc: 
                    t_disapp_pix=int(selpo[3][0])
                    t_disapp_ms=(t_disapp_pix-t0)*frame_to_ms
                else: 
                    t_disapp_pix=-10E6
                    t_disapp_ms=-10E6

                
                if t_pk1_pix>0:
                    residutime=50 #in frames
                    residu_time=min([len(sumtrace), t_pk1_pix+residutime])
                    vesiclecenter=centertrace[t_pk1_pix]
                    vesiclesum=sumtrace[t_pk1_pix]
                    if residu_time<len(sumtrace):
                        residusum=sumtrace[residu_time]
                    else:
                        residusum=-1
                else:
                    vesiclecenter=-1
                    vesiclesum=-1
                    residusum=-1
                
                
                #types
                type='unclassified'
                if t_appear_ms ==-10E6 and t_pk1_ms == -10E6 and t_pk2_ms == -10E6 : type = "rejected"
                if t_appear_ms > -10E6 and t_pk1_ms==-10E6 and t_pk2_ms ==-10E6 and t_disapp_ms > 0 : type = "dock & go"
                if t_appear_ms > -10E6 and t_pk1_ms==-10E6 and t_pk2_ms ==-10E6 and t_disapp_ms == -10E6: type = "dock & stay"
                if t_pk1_ms > -10E6 and t_pk2_ms== -10E6 : type = "single_release"
                if t_pk1_ms> -10E6 and t_pk2_ms> -10E6 : type = "double_release"
                if t_pk2_ms < -10E6 : type = "multiple/other"
                
                print('ms: ', t_appear_ms, t_pk1_ms, t_pk2_ms, t_disapp_ms , ': ', type)

                
                #allocate:
                #this would better go to a json file for each curve to avoid starting all over again....
                json_dict = [{
                    "t_appear_ms": t_appear_ms, 
                    "t_pk1_ms": t_pk1_ms,
                    "t_pk2_ms": t_pk2_ms, 
                    "t_disapp_ms": t_disapp_ms, 
                    "I_tpeak_center_ring": vesiclecenter, 
                    "I_tpeak_allrings": vesiclesum, 
                    "residusum": residusum, 
                    "type": type, 
                    } ]
                with open(out_path / json_name, "w") as f:
                    json.dump( json_dict, f, indent=2)

                plt.close('all')
