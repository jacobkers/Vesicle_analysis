
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
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.optimize import curve_fit

# Define the exponential decay function
def exp_decay(t, A, tau, C):
    return A * np.exp(-t / tau) + C


def fit_exponential_decay(y, n):
    # Create x as index
    x = np.arange(len(y))
    
    # Find index of maximum
    max_index = np.argmax(y)

    # Ensure there are enough points
    if max_index + n >= len(y):
        tau=float('nan')
    else:
        # Extract n points after max
        x_fit = x[max_index + 1 : max_index + 1 + n]
        y_fit = y[max_index + 1 : max_index + 1 + n]

        # Shift x to start from 0
        x_fit_shifted = x_fit - x_fit[0]

        # Initial parameter guesses
        A0 = y_fit[0] - y_fit[-1]
        tau0 = n / 2
        C0 = y_fit[-1]
        p0 = [A0, tau0, C0]

        # Fit the exponential
        popt, _ = curve_fit(exp_decay, x_fit_shifted, y_fit, p0=p0)
        tau=popt[1]
        # Return the decay constant tau
    return tau

def fit_line(y, n=4):
    # Create x as index
    
       
    # Ensure there are enough points
    if  n >= len(y):
        kappa=float('nan')
        b=float('nan')
        t0=float('nan')
    else:   

    # Fit: y = kappa*x + b
        y_slot=y[0:n]
        x_slot = np.arange(len(y_slot))
        kappa, b = np.polyfit(x_slot, y_slot, deg=1)
        t0=-b/kappa

    return kappa, b, t0



def calculate_diffusion_constant_xy(x, y, dt, max_lag=None):
    """
    Calculate 2D diffusion constant from separate x and y arrays.

    Parameters:
    - x, y: numpy arrays of shape (N,)
    - dt: time between samples in seconds
    - max_lag: maximum lag to use (in steps); defaults to N//4

    Returns:
    - D: diffusion constant in pixels²/s
    - msd: mean squared displacement values
    - times: corresponding lag times
    """
    x = np.asarray(x)
    y = np.asarray(y)
    n = len(x)

    if max_lag is None:
        max_lag = n // 4

    msd = []
    times = []

    for lag in range(1, max_lag):
        dx = x[lag:] - x[:-lag]
        dy = y[lag:] - y[:-lag]
        squared_disp = dx**2 + dy**2
        msd.append(np.mean(squared_disp))
        times.append(lag * dt)

    msd = np.array(msd)
    times = np.array(times)

    # Fit the MSD curve to a line: MSD = 4Dt
    slope, intercept, r_value, p_value, std_err = linregress(times, msd)
    D = slope / 4

    return D, msd, times


plot_per_file=1
#read trackmate exports:
datapath='M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/2023_Rafa/2025_06_26_trackmate/'

files=[
'2_TIRF_488_001_PCPG_Chol_trackmate',
'PEG_0.5%_TIRF_488_001_30ms exposure_well1_trackmate',
'PEG_1%_50msExpos_TIRF_488_001_well1_trackmate',
'PEG_2%_50msExpos_TIRF_488_001_well1_mv1_trackmate',
'PEG_5%_50msExpos_TIRF_488_001_well1_vid1_trackmate',
]
legenda=[
    '0% PEG',
    '0.5% PEG',
    '1% PEG',
    '2% PEG',
    '5% PEG',
]
fr2ms_all=[50,54, 68, 68, 68]
pix2um=0.125

if ~ plot_per_file: fig, ax=plt.subplots(2,2)
All_labels=[]
for filname, fr2ms in zip(files,fr2ms_all):
    source=datapath + filname +'.csv'
    traces_df =pd.read_csv((source),delimiter=',')
    trace_IDs=np.unique(traces_df['TRACK_ID'][4:])
    All_labels.append(filname)
    if plot_per_file: fig, ax=plt.subplots(2,2)
    startrow=0
    counter=0
    #single parameters per trace:
    All_trace_IDs=[]
    All_trace_lengths=[]
    All_trace_duration_ms=[]
    All_Diffusions=[]
    All_intensity_drops=[]
    All_Max_brightness=[]
    All_intensity_peaks=[]
    All_time_to_max=[]
    All_flush_times=[]
    All_intensity_vars=[]
    #full trace recors per property:
    data={'time': np.arange(3000)*fr2ms}
    All_traces_intensity=pd.DataFrame(data)

    #loop per trace:
    for trace_ID in trace_IDs:    
            Tu=traces_df["POSITION_T"][startrow:][traces_df['TRACK_ID'][startrow:]==trace_ID]
            Xu=traces_df["POSITION_X"][startrow:][traces_df['TRACK_ID'][startrow:]==trace_ID]
            Yu=traces_df["POSITION_Y"][startrow:][traces_df['TRACK_ID'][startrow:]==trace_ID]
            Iu=traces_df["MEAN_INTENSITY_CH1"][4:][traces_df['TRACK_ID'][startrow:]==trace_ID]
            
            # Zip them together and sort by the first list
            combined = sorted(zip(Tu, Xu, Yu, Iu))

            # Unzip back into three lists
            T_str, X_str, Y_str, I_str = zip(*combined)
            T = [int(float(x)) for x in T_str]
            T=np.array(T_str, dtype=float)
            X = np.array(X_str, dtype=float)
            Y=  np.array(Y_str, dtype=float)
            I=  np.array(I_str, dtype=float)

            #add to full record_per_property (note padding for different lengths)
            I_series = pd.Series(I, index=All_traces_intensity.index[:len(I)])
            All_traces_intensity['trace_'+ str(trace_ID)] = I_series

            if len(T)>2:
                    counter=counter+1
                    if plot_per_file:
                            ax[0,0].plot(T-T[0],X-X[0])
                            ax[0,0].set_xlabel('time, frames')
                            ax[0,0].set_ylabel('x-position, pixels')
                            ax[0,1].plot(T-T[0],I)
                            ax[0,1].set_xlabel('time, frames')
                            ax[0,1].set_ylabel('intensity, a.u')
                    #diffusion:
                    if len(T)>4:
                            D, msd, times=calculate_diffusion_constant_xy(X, Y, 1, max_lag=4)
                    else:
                            D= float('nan')
                    All_Diffusions.append(D*(pix2um**2)/(fr2ms/1000))  #in mu^2/s
                    #peak behavior:
                    Max_brighness=np.max(I)
                    t_max=np.argmax(I)
                    
                    All_time_to_max.append(t_max*fr2ms)
                    All_Max_brightness.append(Max_brighness)
                    intensity_drop=(Max_brighness-np.mean(I[-3:-1]))/Max_brighness*100
                    intensity_peak=(Max_brighness-I[0])/Max_brighness*100
                    intensity_var=np.std(I)/np.mean(I)*100
                    kappa, b, t0 = fit_line(I[t_max:], n=8)
                    
                    All_trace_lengths.append(len(T))
                    All_trace_duration_ms.append(len(T)*fr2ms)
                    All_trace_IDs.append(trace_ID)
                    All_intensity_drops.append(intensity_drop)
                    All_intensity_peaks.append(intensity_peak)        
                    All_intensity_vars.append(intensity_var)                         
                    All_flush_times.append(t0*fr2ms)
                    

    if plot_per_file:
            ax[1,0].hist(All_Diffusions, bins=20, color='skyblue', edgecolor='k')
            ax[1,0].set_xlabel('D, mu^2/s')
            ax[1,0].set_ylabel('counts')

            ax[1,1].hist(All_intensity_vars, bins=20, color='red', edgecolor='k')
            ax[1,1].set_xlabel('intensity variation,%')
            ax[1,1].set_ylabel('counts')  
    
            fig.show()
            print(counter)
            plt.savefig(datapath + filname + '_proc_histograms.png')  # You can also use .pdf, .svg, .jpg, etc.
            plt.close('all')

    if plot_per_file ==0:
            ax[0,0].plot(All_Diffusions, All_trace_duration_ms, 'o', markersize=2)
            ax[0,0].set_xlabel('D, mu^2/s')
            ax[0,0].set_xscale('log')
            ax[0,0].set_yscale('log')
            ax[0,0].set_ylabel('duration, ms')
            ax[0,0].legend(legenda)

            ax[0,1].plot(All_Diffusions, All_flush_times, 'o', markersize=2)
            ax[0,1].set_xlabel('D, mu^2/s')
            ax[0,1].set_xscale('log')
            ax[0,1].set_yscale('log')
            ax[0,1].set_ylabel('flush time, ms')
            #ax[0,0].legend(All_labels)
            
            ax[1,0].plot(All_Diffusions, All_intensity_vars, 'o', markersize=2)
            ax[1,0].set_xlabel('D, mu^2/s')
            ax[1,0].set_xscale('log')
            ax[1,0].set_yscale('log')
            ax[1,0].set_ylabel('I_variation, %')

            ax[1,1].plot(All_trace_duration_ms, All_intensity_vars, 'o', markersize=2)
            ax[1,1].set_xlabel('duration, ms')
            ax[1,1].set_xscale('log')
            ax[1,1].set_yscale('log')
            ax[1,1].set_ylabel('I_variation, %')
            fig.tight_layout()
    
            #plot and save:
            #fig.tight_layout()
            fig.show()
            plt.savefig(datapath +'T00_all_data' + '_parameters_per_trace.png')  # You can also use .pdf, .svg, .jpg, etc.
            dum=1
    #plt.close('all')

    #crop and save the per-record_data:
    lengths = All_traces_intensity.iloc[:, 1:].notna().sum()
    # 2️⃣  Find the maximum trace length
    max_len = lengths.max()
    print(f"Longest trace length: {max_len}")
    # 3️⃣  Crop the DataFrame to that many rows
    All_traces_intensity_cropped = All_traces_intensity.iloc[:max_len].copy()
    # 2️⃣  Sort the column names by those lengths (descending or ascending)
    sorted_cols = [All_traces_intensity_cropped.columns[0]] + list(lengths.sort_values(ascending=False).index)
    # 3️⃣  Reorder the DataFrame columns
    All_traces_intensity_sorted = All_traces_intensity_cropped[sorted_cols].copy()
    csv_target1=(datapath + 'T00_' + filname +'_all_traces_intensities.csv')
    All_traces_intensity_sorted.to_csv(csv_target1, index=False)
    
    #make an export data frame for the single parameters:
    events_df = pd.DataFrame()
    events_df['trace_ID'] = All_trace_IDs  
    events_df['trace_length,frs'] = All_trace_lengths 
    events_df['trace_duration, ms'] = All_trace_duration_ms 
    events_df['time_to_max, ms'] = All_time_to_max # Example values
    events_df['flush_time, ms'] = All_flush_times # Example values
    events_df['Diffusion, mu^2/s'] = All_Diffusions 
    events_df['Max_brightness'] = All_Max_brightness 
    events_df['intensity_peaks%'] = All_intensity_peaks # Example values
    events_df['intensity_drop%'] = All_intensity_drops # Example values
    events_df['intensity_var%'] = All_intensity_vars # Example values
    
    xls_target2=(datapath + 'T00_' + filname +'_parameters_per_trace.xlsx')
    events_df.to_excel(xls_target2, index=False)

    print(f"\nUpdated data has been written to target")