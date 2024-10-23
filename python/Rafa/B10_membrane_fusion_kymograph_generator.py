import numpy as np
import cv2
import math as mt
from skimage import io
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tf
from common_tools import guv_tools


def load_tiff_movie(input_path):
    """Load a TIFF movie as a list of frames."""
    with Image.open(input_path) as img:
        frames = []
        while True:
            frames.append(img.copy())
            try:
                img.seek(img.tell() + 1)
            except EOFError:
                break
    return frames


# Example usage
if 0: 
    label='2_TIRF_488_001_PCPG_Chol_small_short'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short.tif'
if 1:
    label='2_TIRF_488_001_PCPG_Chol_long'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol.tif'
if 0:
    moviepath= Path.cwd()
    movie_filename = '40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1_red.tif'
    filename = 'MAX_40 uM LUVsWITHCerC6_RealTime_Series002_t000_crp-1.tif (red).tif'

image_path =  moviepath/ filename
movie_path =  moviepath/ movie_filename


#load movie:
frames=load_tiff_movie(movie_path)
frames_array=[]
for frame in frames:
   frames_array.append(np.array(frame))
frames_array=np.array(frames_array)


#load events
event_data_name=label +"_events" +  str(".csv")
csv_events=savepath /  event_data_name
csv_path_in = Path(csv_events)
event_data = np.loadtxt(csv_events, delimiter=';')

rws=[0,1]
DT_list=[100, 20000]
pre_shift_list=[10,200000]
 
DX=70 
DY=70

for event_no, event in enumerate(event_data): 
    fig, ax=plt.subplots(4,1)   
    for rw, DT, pre_shift in zip(rws, DT_list, pre_shift_list):   
        x0=int(event[1])
        y0=int(event[2])
        t0=np.max([0, int(event[0])+int(DT/2)-pre_shift])
        subarray, t_min, t_max, x_min, x_max, y_min, y_max=guv_tools.extract_subarray(frames_array, t0, x0, y0, DT, DX, DY)
        #sum:
        sumprojection_0=np.sum(subarray,axis=0)
        sumprojection_1=np.sum(subarray,axis=1) #keeps y around Y0
        sumprojection_2=np.sum(subarray,axis=2) #keeps x around X0

        #choose full side if close to edge
        rr,cc= np.shape(sumprojection_0)
        if rr>cc:
            used_proj=sumprojection_2
            used_trace=np.sum(sumprojection_2.T,axis=0)
            pos_min=y_min
            pos_max=y_max
        else:
            used_proj=sumprojection_1
            used_trace=np.sum(sumprojection_1.T, axis=0)
            pos_min=x_min
            pos_max=x_max
        #show:
        if rw == 0:  #zoom
            ax[0].imshow(sumprojection_0, extent=[x_min,x_max,y_min, y_max])
            ax[0].set_title('SUM_event' + str(event_no).zfill(4))
            ax[3].imshow(used_proj.T, aspect='auto', extent=[t_min,t_max,pos_min,pos_max])
            ax[3].set_ylabel("pos, pixels")
            ax[3].set_xlabel("Time,frames")
            t_start=t_min
            t_stop=t_max
        if rw == 1: #overview
            ax[1].plot(used_trace)
            ax[1].set_ylabel("sum intensity, a.u.")
            ax[1].autoscale(enable=True, axis='x', tight=True)
            ax[1].get_xaxis().set_visible(False)
            #white lines
            
            ax[2].imshow(used_proj.T,aspect='auto', extent=[t_min,t_max,pos_min,pos_max,])
            ax[2].plot([t_start,t_start],[pos_min,pos_max], 'w--',linewidth=0.5)
            ax[2].plot([t_stop,t_stop],[pos_min,pos_max], 'w--',linewidth=0.5)
            ax[2].set_ylabel("pos, pixels")

        fig.tight_layout()
        #final savings:
        if rw==1:
            #fig.tight_layout()
            #fig.show()
            #jpeg overview:
            kymo_overview_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_kymo.png")
            kymo_path= savepath/  kymo_overview_name
            fig.savefig(kymo_path)
        
        if 0:
            #tiff files:
            kymo0_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_XY.tif")
            kymo0_path= savepath/  kymo0_name
            #io.imsave(savepath/  kymo0_name, sumprojection_0)
            io.imsave(savepath / f"{kymo0_name}", sumprojection_0, check_contrast=False)

            kymo1_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_XT.tif")
            kymo1_path= savepath/  kymo0_name
            #io.imsave(savepath/  kymo0_name, sumprojection_0)
            io.imsave(savepath / f"{kymo1_name}", sumprojection_1, check_contrast=False)
            dum=1

            kymo2_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_YT.tif")
            kymo2_path= savepath/  kymo0_name
            #io.imsave(savepath/  kymo0_name, sumprojection_0)
            io.imsave(savepath / f"{kymo2_name}", sumprojection_2, check_contrast=False)
            dum=1
    plt.close('All')    



    







