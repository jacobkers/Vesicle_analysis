import numpy as np
import csv
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from scipy.optimize import curve_fit
from common_tools import guv_tools


# exponential function with background
def exponential_model(t, A, k, B, t0):
    return A * np.exp(-k * (t - t0)) + B

class Event:
    def __init__(self):
        self.index = 0
        self.x0 = 0
        self.y0 = 0
        self.t0 = 0
        self.type = 0

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

def fusion():
    # Example usage
    if 0: 
        label='2_TIRF_488_001_PCPG_Chol_small_short'
        moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
        savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short.tif'
        filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short.tif'
        xls_classification = savepath / "Events_classification_jacob_short.xlsx"  
    if 1:
        label='2_TIRF_488_001_PCPG_Chol_long'
        moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
        savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        movie_filename = '2_TIRF_488_001_PCPG_Chol.tif'
        filename ='STD_2_TIRF_488_001_PCPG_Chol.tif'
        xls_classification  = savepath / "Events_classification_jacob.xlsx"  
    if 0:
        moviepath= Path.cwd()
        movie_filename = '40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1_red.tif'
        filename = 'MAX_40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1.tif (red).tif'

    image_path =  moviepath/ filename
    movie_path =  moviepath/ movie_filename


    #load traces
    trace_data_name=label +"_traces" +  str(".csv")
    csv_traces=savepath /  trace_data_name
    csv_path_in = Path(csv_traces)
    print(csv_traces.stem)
    pre_trace_data = np.loadtxt(csv_traces, delimiter=';')

    #load classification file of events (contains t0,x,y,type)
    xls_source = savepath / xls_classification 
    wb = load_workbook(filename = xls_classification)
    sheet_events = wb['events']
    ColNames = {}
    Current  = 0
    for COL in sheet_events.iter_cols(1, sheet_events.max_column):
        ColNames[COL[0].value] = Current
        Current += 1
    event_list=[]
    for row_cells in sheet_events.iter_rows(min_row=2):
        event=Event()
        event.index=((row_cells[ColNames['event']].value))
        event.type=((row_cells[ColNames['type']].value))
        event.x0=((row_cells[ColNames['x']].value))
        event.y0=((row_cells[ColNames['y']].value))
        event.t0=((row_cells[ColNames['t0']].value))
        event_list.append(event)

    #we need to add:
    # dark treshold
    # end-of-trace residu
    # dock time
    # event starts (maxima)
    # release times (minima)
    # end-of-event (=eot or back-to-dark)

    # plot traces and start_time
    xls_source = savepath / xls_source 
    frs,N_events=np.shape(pre_trace_data)

    
    for event,pre_trace in zip(event_list,pre_trace_data.T):
        # start of rise:
        t_maxrise=int(event.t0)

        # get background:
        inliers, outliers, flags=guv_tools.outlier_flag(data=pre_trace[0:t_maxrise], tolerance=3, sig_change=0.7, how=1, sho=0, demo=0)
        I_tresh=np.median(inliers)+2*np.std(inliers)


        #first detection:
        t_begin=travel_from_start(pre_trace, t_maxrise, I_tresh, direction=-1)
        t_end=travel_from_start(pre_trace, t_maxrise, I_tresh, direction=1)
        
        # analyze differential trace
        dif_trace=np.diff(pre_trace)
        dif_in, dif_out, flags=guv_tools.outlier_flag(data=dif_trace, tolerance=2, sig_change=0.7, how=-1, sho=0, demo=0)
        drop_tres=np.mean(dif_in)-4*np.std(dif_in)
        
        # Run the function
        drop_indices = find_steep_drops(pre_trace,t_maxrise, I_tresh, drop_tres)


        t1a=np.argmin(dif_trace[t_begin:t_end])
        t1=t_begin+t1a
        
        tp=event.type
        start=np.max([t_maxrise-20, 0])
        start=0 
        stop=np.min([t_maxrise+100, frs])
        trace_cut=pre_trace[start:stop]
        dif_trace_cut=dif_trace[start:stop]
        
        print(event.index, t_maxrise-t_begin,t_end-t_maxrise)
        
        #show:
        if  1: #tp== "hemifusion":
            fig, ax=plt.subplots(2,2)
            ax[0,0].plot(pre_trace, '-', markersize=2)
            ax[0,0].plot(t_maxrise,pre_trace[t_maxrise], 'ro-', markersize=8)
            ax[0,0].plot(t_begin,pre_trace[t_begin], 'ko-', markersize=4)
            ax[0,0].plot(t_end,pre_trace[t_end], 'mo-', markersize=4)
            ax[0,0].set_title('traces')
            ax[0,1].plot(dif_trace, '-', markersize=2)
            ax[0,1].plot(t_maxrise, dif_trace[t_maxrise], 'ro-', markersize=4)
            ax[0,1].plot(t1, dif_trace[t1], 'go-', markersize=4)
            ax[0,1].plot(drop_indices,dif_trace[drop_indices], 'bo', markersize=4)
            ax[0,1].set_title('derivative')
            ax[1,0].plot(trace_cut, '-')
            ax[1,0].set_title('aligned')
            ax[1,1].plot(trace_cut/np.max(trace_cut), '-')
            ax[1,1].set_title('normalized')
            fig.show()
            dum=1
            plt.close('all')


        







