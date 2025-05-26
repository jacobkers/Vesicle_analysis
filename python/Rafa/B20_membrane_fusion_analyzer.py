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
from Rafa.B00_init import get_exps

def pick_combination_indices_with_full(array):
    # Generate all possible combinations of 3 indices
    indices = range(len(array))
    combinations_list = list(combinations(indices, 4))    
    # Add the full set of indices as the last tuple
    combinations_list.append(tuple(indices))   
    return combinations_list

# exponential function with background
def exponential_model(t, A, k, B, t0):
    return A * np.exp(-k * (t - t0)) + B

class Event:
    def __init__(self):
        self.index = 0
        self.x0 = 0
        self.y0 = 0
        self.t0 = 0
        self.type = 0  #user info

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

def find_steep_drops(trace, idx0, I_thresh, drop_threshold, max_drops=20):
    """ start with a one-dimensional array of intnesity trace points with, 
    for example a length of 225 points and a starting index idx0 pointing to an element of this array (say, idx0=14). 
    Use the derivative of this intensity trace to find a limited number (<5) of indices idxs_down 
    that exhibit a steep downward intensity drop, sorted by their index. 
    These drops should be associated with local minima in the derivative trace. 
    Include only indices from a higher index than idx0. Include only indices where the intensity 
    is above a certain treshold level I_tresh. 
    The data may be a bit noisy (S/N~10): please ignore local noice rises and drops. 
     """

    # Smooth the trace using a moving average to reduce noise
    window_size = 2  # Adjustable parameter for noise smoothing
    smoothed_trace = np.convolve(trace, np.ones(window_size)/window_size, mode='same')
    
    # Compute the derivative of the smoothed trace
    derivative = np.diff(smoothed_trace)
    #derivative = np.diff(trace)
    
    deriv_noise=np.std(derivative[1:])

    # Search for local minima in the derivative trace from idx0 onward
    idxs_down = []
    
    for i in range(idx0, len(derivative) - 2):  # Ensure we don't go out of bounds
        # Check if it's a local minimum in the derivative and satisfies conditions
        if (derivative[i] < derivative[i-1] and derivative[i] < derivative[i+1] and 
        abs(derivative[i]-derivative[i-1])>1*deriv_noise and abs(derivative[i]-derivative[i+1])>1*deriv_noise and
        derivative[i] < -drop_threshold and trace[i] > I_thresh):
            idxs_down.append(i)
            if len(idxs_down) >= max_drops:
                break
                
    return idxs_down

def fusion(exps):
    for initval in exps:
        label=initval.unique_label
        moviepath=initval.moviepath
        savepath=initval.savepath
        movie_filename = initval.movie_filename
        filename =initval.spot_image    
        data_source_path=initval.moviepath
        xls_classification = initval.savepath / initval.xls_classification_file

        pix2um=0.1254
        frame_to_ms=50
        
        """ 
        Ring sizes are calculated such that each covers the same area as the central disk (with radius R0)
        R0=10
        rings=[0, R0]
        if 1: #equal surface
            for i in np.arange(4):
                Ri=rings[i+1]
                R_nxt=(Ri**2+R0**2)**0.5
                rings.append(R_nxt)

        used ring sizes (mean)
        mean
        5.00
        12.07
        15.73
        18.66
        21.18 """

        ring_radii_pix=[5,12.07,15.73,18.66,21.18]
        ring_radii_mu=[]
        ring_areas_musq=[]
        for ri, Ri_pix in enumerate(ring_radii_pix):
            ring_radii_mu.append(Ri_pix*pix2um)
            if ri==0:
                area=(np.pi*(Ri_pix*pix2um)**2)
            else:
                Ri_pix0=ring_radii_pix[ri-1]
                area=(np.pi*(Ri_pix*pix2um)**2-
                    np.pi*(Ri_pix0*pix2um)**2)
            ring_areas_musq.append(area)
            

        #load pre-traces
        #
        trace_data_name="B00_"+ label +"_traces" +  str(".csv")
        csv_traces=initval.savepath /  trace_data_name
        csv_path_in = Path(csv_traces)
        print(csv_traces.stem)
        pre_trace_data = np.loadtxt(csv_traces, delimiter=';')

        #load pre events (x,y,start) (from B10)
        events_data_name="B00_"+ label +"_events" +  str(".csv")
        csv_events=initval.savepath /  events_data_name
        csv_path_in = Path(csv_events)
        pre_event_data = np.loadtxt(csv_events, delimiter=';')
        # Define custom column names
        column_names = ['index', 't0', 'x0', 'y0', 'I_t0_jump']
        # Create a DataFrame with custom column names
        events_df = pd.DataFrame(data=pre_event_data, columns=column_names)
  
        #OR load classification file of events (contains t0,x,y,type)
        xls_source = initval.savepath / xls_classification 
        wb = load_workbook(filename = xls_classification)
        sheet_events = wb['events']
        ColNames = {}
        Current  = 0

        for COL in sheet_events.iter_cols(1, sheet_events.max_column):
            ColNames[COL[0].value] = Current
            Current += 1
        
        # plot traces and start_time
        xls_source = initval.savepath / xls_source 
        frs,N_events=np.shape(pre_trace_data)
        all_ring_peak_t=[]
        save_data=[]
        for evi,pre_trace in enumerate(pre_trace_data.T):
            print("B20_event:" + str(evi))
            #collect ring traces of this event
            trace_data_name='B10_kymographs_' + label +'/csv/' + 'event' + str(evi).zfill(4) +  str("_ring_traces_intensity.csv")
            csv_ring_traces=initval.savepath /  trace_data_name
            ring_traces = np.loadtxt(csv_ring_traces, delimiter=';')

            fig, ax=plt.subplots(2,1)
            ring_peak_t=[]
            ring_squ_rad_mu=[]
            for ring_i, ring_trace in enumerate(ring_traces.T):
                if ring_i==0:
                    ring_trace_sum=ring_trace
                    ring_trace_center=ring_trace
                else:
                    ring_trace_sum=ring_trace_sum+ring_trace

                #tr=relative time, ta=absolute 
                ta_maxrise=int(events_df.iloc[evi]["t0"])  # start of rise, initial detection:
                lo=np.min([ta_maxrise, 60])
                hi=np.min([len(ring_trace)-ta_maxrise, 60])
                tr_maxrise=lo

                #we only look in a range around the event:
                
                zoomsection=list(range(ta_maxrise-lo,ta_maxrise+hi))  
                zoomax=np.arange(-lo, -lo+len(zoomsection))*frame_to_ms         
                ring_trace_r=ring_trace[zoomsection]
                diff_ring=np.diff(ring_trace_r)

                tr_maxdrop=  np.argmin(diff_ring)+1   #relative      
                if ring_i==0: #find precise starting time
                    tr_maxrise2_discrete=  np.argmax((diff_ring))   #relative, we favor big jumps early  
                    #subpixel step for diff
                    spx2=guv_tools.subpix_step(diff_ring[tr_maxrise2_discrete-1:tr_maxrise2_discrete+2])
                    tr_maxrise2=tr_maxrise2_discrete+spx2+1

                    inliers, outliers, flags=guv_tools.outlier_flag(data=ring_trace_r[0:tr_maxrise], tolerance=3, sig_change=0.7, how=1, sho=0, demo=0)
                    I_tresh=np.min(ring_trace_r)+0.05*(np.max(ring_trace_r)-np.min(ring_trace_r))

                    #first detection:
                    t_begin_r=travel_from_start(ring_trace_r, tr_maxrise, I_tresh, direction=-1)-1

                ta_maxdrop=   tr_maxdrop - lo + ta_maxrise                   #absolute

                #find the first maximum before the steepest drop:
                tr_pk=find_peak_from(ring_trace_r,tr_maxdrop, direction=-1, max_or_min=1)
                spx=guv_tools.subpix_step(ring_trace_r[tr_pk-1:tr_pk+2])   #subpixel step
                tr_pk_spx=tr_pk+spx
                

                #collect some values:
                ring_peak_t.append(tr_pk_spx)
                ring_squ_rad_mu.append(ring_radii_mu[ring_i]**2)


                #building data set:
                if ring_i==0:
                    ta_maxdrop_ring0=ta_maxdrop #to be used later on
                    this_event_savedata= [
                        events_df.iloc[evi]["index"],                                   #transfer info:
                        events_df.iloc[evi]["x0"],
                        events_df.iloc[evi]["y0"],
                        events_df.iloc[evi]["t0"],
                        np.round((t_begin_r-tr_maxrise2)*frame_to_ms),      # "r0_first appearance"
                        0,                                                  # "r0_rise (=zero per definition)"
                        np.round((tr_pk_spx-tr_maxrise2)*frame_to_ms),      # "r0_mainpeak"
                        np.round((tr_maxdrop -tr_maxrise2)*frame_to_ms),    # "r0_maindrop"
                    ]

                    ax[0].plot((t_begin_r-lo)*frame_to_ms,ring_trace_r[t_begin_r], 'bo-', markersize=8)
                    ax[0].plot((tr_maxrise2-lo)*frame_to_ms,ring_trace_r[tr_maxrise+1], 'rx-', markersize=8)
                    
                if ring_i>0: 
                    this_event_savedata.append(
                        np.round((tr_pk_spx-tr_maxrise2)*frame_to_ms))      #"r1(2,3,4)_mainpeak"
                ax[0].plot((tr_pk_spx-lo)*frame_to_ms,ring_trace_r[tr_pk], 'go-', markersize=4) #ring peaks  
                ax[0].plot((tr_maxdrop-lo)*frame_to_ms,ring_trace_r[tr_maxdrop], 'kx-', markersize=8)  
                ax[0].plot(zoomax, ring_trace_r, 'o-', markersize=2)
            
            #----------------------------------------------------------------------------
            #a bit of analysis on the center ring signal:
            # find the first maximum in the CENTER trace before the steepest drop of the CENTER trace:
            ta_pk_center=find_peak_from(ring_trace_center,ta_maxdrop_ring0, direction=-1, max_or_min=1)
            
            centerval_min=np.min(ring_trace_center)
            centerval_peak=ring_trace_center[ta_pk_center]-centerval_min
            if ta_pk_center + 10<len(ring_trace_sum):
                perc_residu10frs=np.round((ring_trace_center[ta_pk_center+10]-centerval_min)/centerval_peak*100)
            else:
                perc_residu10frs=np.nan
            if ta_pk_center + 20<len(ring_trace_sum):
                perc_residu20frs=np.round((ring_trace_center[ta_pk_center+20]-centerval_min)/centerval_peak*100)
            else:
                perc_residu20frs=np.nan
            if ta_pk_center + 40<len(ring_trace_center):
                perc_residu40frs=np.round((ring_trace_center[ta_pk_center+40]-centerval_min)/centerval_peak*100)
            else:
                perc_residu40frs=np.nan
            #add to event data:
            this_event_savedata.append(centerval_peak)    # 
            this_event_savedata.append(perc_residu10frs)  # 
            this_event_savedata.append(perc_residu20frs)  # 
            this_event_savedata.append(perc_residu40frs)  # 

            #-------------------------------------------------------------------------
            #Diffusion further analysis on peaks, with possibility to drop 1 point:
            diff_peak_t_s=(ring_peak_t-ring_peak_t[0])*frame_to_ms/1000
            #pick a random set of the four points:
            all_picks_idxes= pick_combination_indices_with_full(ring_peak_t)
            r_value_best=0
            slope_best=0
            zero_crossing_best=0
            #determine diffusion constant by a linear fit on the squared ring sizes vs peak times;
            #for this, choose the best fit for three-or four pointpicks (and keep track of which points were used)
            for indices in all_picks_idxes:
                try_t=[diff_peak_t_s[i] for i in indices]
                try_pk=[ring_squ_rad_mu[i] for i in indices]
                slope, intercept, r_value, p_value, std_err = linregress(try_t, try_pk)
                r_squared = r_value**2 # Calculate R² value
                zero_crossing = -intercept / slope # Calculate zero-crossing (x-intercept)
                if r_value>r_value_best:
                    slope_best=slope
                    zero_crossing_best=zero_crossing
                    r_squared_best=r_squared
                    usedcode=99
                    for ix in indices:
                        usedcode=10*usedcode+ix   
            #add to event data:
            this_event_savedata.append(np.round(slope_best/4,2))  # diffusion constant
            this_event_savedata.append(np.round(r_squared_best,2))  # goodness of fit
            this_event_savedata.append(np.round(zero_crossing_best,2))  # goodness of fit
            this_event_savedata.append(usedcode)                    # "use_4diff"

            ax[0].set_title('trace' + str(evi).zfill(4))
            ax[0].legend(['begin', 'max_rise_subpix','peak_subpix','maxdrop'],loc='upper right')
            ax[0].set_xlabel('relative time, ms')
            ax[0].set_ylabel('ring sum, a.u')
            all_ring_peak_t.append(ring_peak_t)
            #for old_ring in all_ring_peak_t:
            #    ax[1].plot(ring_radii, old_ring, 'o-',markersize=2)         
            ax[1].plot((t_begin_r-tr_maxrise2)*frame_to_ms,0, 'bo')
            ax[1].plot((tr_maxrise2-tr_maxrise2)*frame_to_ms,0, 'rx-')
            ax[1].plot((ring_peak_t-tr_maxrise2)*frame_to_ms, ring_squ_rad_mu, 'go-')
            ax[1].legend(['begin', 'max_rise_subpix', 'ring_peaks'],loc='upper left')
            ax[1].set_xlabel('relative time, ms')
            ax[1].set_ylabel('(ring R^2, mu^2')
            #ax[1].set_ylim(55,70)
            fig.tight_layout()
            fig.show()
            

            #savings:
            save_data.append(this_event_savedata)

            plot_path = initval.savepath / str('B20_peak_analysis_' + label +'/')
            if not plot_path.is_dir():
                plot_path.mkdir()

            plot_name=str('B20_peak_analysis_') + label +'/' + 'event' + str(evi).zfill(4) +  str("_release_analysis.png")
            plot_target=initval.savepath /  plot_name
            fig.savefig(plot_target)
            plt.close('all')

            #save collected data
            # 
        #now: ["index","type","first appearance", "rise" ,"peak", "drop","use_it"]
        #to add, all in ms:
        hdr=[
        "event",
        "x0",
        "y0",	
        "t0",
        "t_r0_first appearance", 
        "t_r0_rise" ,
        "t_r0_mainpeak",  
        "t_r0_maindrop",
        "t_r1_mainpeak",
        "t_r2_mainpeak",
        "t_r3_mainpeak",
        "t_r4_mainpeak",
        "I_center_peakval",
        "I_center_residu10frs_perc",
        "I_center_residu20frs_perc",
        "I_center_residu40frs_perc",
        "fit_D_mu^2/s",
        "fit_R2_value",
        "fit_zero_crossing",
        "fit_use_it_4diff",
        ]

        event_data_name='B20_peak_analysis_' + label +'/' + 'B20_event_times.csv'
        csv_target=initval.savepath /  event_data_name
        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
            # create the csv writer
            writer = csv.writer(csv_f, delimiter=";")
            writer.writerow(hdr)
            for data_row in save_data:         
                writer = csv.writer(csv_f, delimiter=";")
                writer.writerow(data_row)
