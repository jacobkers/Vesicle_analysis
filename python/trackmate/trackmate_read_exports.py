
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

# Example usage:
# xy = np.array([[x0, y0], [x1, y1], ..., [xN, yN]])
# dt = 0.1  # seconds per frame
# D, msd, times = calculate_diffusion_constant(xy, dt)

# Optionally plot:
# plt.plot(times, msd, 'o', label='MSD')
# plt.plot(times, 4*D*times, '-', label=f'Fit: D={D:.3f} px²/s')
# plt.xlabel('Time (s)')
# plt.ylabel('MSD (px²)')
# plt.legend()
# plt.show()


plot_per_file=0
#read trackmate exports:
datapath='M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/2023_Rafa/2025_06_26_trackmate/'
if 0:
    files=[
    'PEG_0.5%_TIRF_488_001_30ms exposure_trackmate',
    'PEG_1%_50msExpos_TIRF_488_001_trackmate',
    '2_TIRF_488_001_PCPG_Chol_trackmate',
    ]
    legenda=[
        '0.5% PEG',
        '1% PEG',
        'Rafa_hiQTirf',
    ]
else: 
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

if ~ plot_per_file: fig, ax=plt.subplots(2,2)
All_labels=[]
for filname in files:
    source=datapath + filname +'.csv'
    traces_df =pd.read_csv((source),delimiter=',')
    trace_IDs=np.unique(traces_df['TRACK_ID'][4:])
    All_labels.append(filname)
    if plot_per_file: fig, ax=plt.subplots(2,2)
    startrow=0
    counter=0
    All_trace_IDs=[]
    All_trace_lengths=[]
    All_Diffusions=[]
    All_intensity_drops=[]
    All_Max_brightness=[]
    All_decays=[]
    All_intensity_peaks=[]
    All_time_to_max=[]
    All_flush_times=[]

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
                    All_Diffusions.append(D)
                    #peak behavior:
                    Max_brighness=np.max(I)
                    t_max=np.argmax(I)
                    All_time_to_max.append(t_max)
                    All_Max_brightness.append(Max_brighness)
                    intensity_drop=(Max_brighness-np.mean(I[-3:-1]))/Max_brighness*100
                    intensity_peak=(Max_brighness-I[0])/Max_brighness*100
                    kappa, b, t0 = fit_line(I[t_max:], n=8)
                    
                    All_trace_lengths.append(len(T))
                    All_trace_IDs.append(trace_ID)
                    All_intensity_drops.append(intensity_drop)
                    All_intensity_peaks.append(intensity_peak)                       
                    All_decays.append(-kappa)
                    All_flush_times.append(t0)
                    

    if plot_per_file:
            ax[1,0].hist(All_Diffusions, bins=20, color='skyblue', edgecolor='k')
            ax[1,0].set_xlabel('D, pix^2/fr')
            ax[1,0].set_ylabel('counts')

            ax[1,1].hist(All_intensity_drops, bins=20, color='red', edgecolor='k')
            ax[1,1].set_xlabel('intensity drop,%')
            ax[1,1].set_ylabel('counts')  
    
            dum=1
            fig.show()
            print(counter)
            plt.savefig(datapath + filname + '_proc_histograms.png')  # You can also use .pdf, .svg, .jpg, etc.
            plt.close('all')

    if plot_per_file ==0:
            ax[0,0].plot(All_Diffusions, All_trace_lengths, 'o', markersize=2)
            ax[0,0].set_xlabel('D, pix^2/fr')
            ax[0,0].set_xscale('log')
            ax[0,0].set_yscale('log')
            ax[0,0].set_ylabel('lengths, frs')
            ax[0,0].legend(legenda)

            ax[0,1].plot(All_Diffusions, All_flush_times, 'o', markersize=2)
            ax[0,1].set_xlabel('D, pix^2/fr')
            ax[0,1].set_xscale('log')
            ax[0,1].set_yscale('log')
            ax[0,1].set_ylabel('flush time, frs')
            #ax[0,0].legend(All_labels)
            
            ax[1,0].plot(All_Diffusions, All_Max_brightness, 'o', markersize=2)
            ax[1,0].set_xlabel('D, pix^2/fr')
            ax[1,0].set_xscale('log')
            ax[1,0].set_yscale('log')
            ax[1,0].set_ylabel('peak brightness, a.u.')

            ax[1,1].plot(All_Diffusions, All_time_to_max, 'o', markersize=2)
            ax[1,1].set_xlabel('D, pix^2/fr')
            ax[1,1].set_xscale('log')
            ax[1,1].set_yscale('log')
            ax[1,1].set_ylabel('time_to_max, frams')
            fig.tight_layout()
            #fig.tight_layout()
            fig.show()
            plt.savefig(datapath +'all_data' + '_proc_motility_vs_release.png')  # You can also use .pdf, .svg, .jpg, etc.
            
    #plt.close('all')
    dum=1
    #make an export data frame:
    events_df = pd.DataFrame()
    events_df['trace_ID'] = All_trace_IDs  # Example values
    events_df['trace_length,frs'] = All_trace_lengths # Example values
    events_df['Diffusion, pix2/fr'] = All_Diffusions # Example values
    events_df['Max_brightness'] = All_Max_brightness # Example values
    events_df['intensity_peaks%'] = All_intensity_peaks # Example values
    events_df['intensity_drop%'] = All_intensity_drops # Example values
    events_df['decay_1storder'] =All_decays # Example values
    events_df['time_to_max, frs'] = All_time_to_max # Example values
    events_df['flush_time, frs'] = All_flush_times # Example values
    
    xls_target=(datapath + filname +'_proc.xlsx')

    # Write the updated data to a new Excel file
    events_df.to_excel(xls_target, index=False)

    print(f"\nUpdated data has been written to target")