import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt


# Example usage
if 0: 
    label='2_TIRF_488_001_PCPG_Chol-1_small_short'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
if 1:
    label='2_TIRF_488_001_PCPG_Chol_long'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol.tif'
if 0:
    moviepath= Path.cwd()
    movie_filename = '40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1_red.tif'
    filename = 'MAX_40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1.tif (red).tif'

image_path =  moviepath/ filename
movie_path =  moviepath/ movie_filename


#load traces
trace_data_name=label +"_traces" +  str(".csv")
csv_traces=moviepath /  trace_data_name
csv_path_in = Path(csv_traces)
print(csv_traces.stem)
trace_data = np.loadtxt(csv_traces, delimiter=';')

#load events
event_data_name=label +"_events" +  str(".csv")
csv_events=moviepath /  event_data_name
csv_path_in = Path(csv_events)
event_data = np.loadtxt(csv_events, delimiter=';')

# plot traces and start_time
frs,N_events=np.shape(trace_data)

fig, ax=plt.subplots(2,2)
for event,trace in zip(event_data,trace_data.T):
    dif_trace=np.diff(trace)
    #mxi=np.argmax(dif_trace)
    mxi=int(event[0])
    start=np.max([mxi-20, 0])
    stop=np.min([mxi+50, frs])
    trace_cut=trace[start:stop]
    dif_trace_cut=dif_trace[start:stop]

    #show:
    if np.max(trace)>0.2E6:
        ax[0,0].plot(trace, '-', markersize=2)
        ax[0,0].plot(mxi,trace[mxi], 'ro-', markersize=4)
        ax[0,0].set_title('traces')
        ax[0,1].plot(dif_trace, '-', markersize=2)
        ax[0,1].plot(mxi, dif_trace[mxi], 'ro-', markersize=4)
        ax[0,1].set_title('derivative')
        ax[1,0].plot(trace_cut, '-')
        ax[1,0].set_title('aligned')
        ax[1,1].plot(trace_cut/np.max(trace_cut), '-')
        ax[1,1].set_title('normalized')
        fig.show()
        dum=1
plt.close('all')


    







