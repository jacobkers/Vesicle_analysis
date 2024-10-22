import numpy as np
import cv2
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
if 1: 
    label='2_TIRF_488_001_PCPG_Chol_small_short'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short.tif'
if 0:
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


DT=75 
DX=30 
DY=30
pre_shift=25
for event_no, event in enumerate(event_data):
    fig, ax=plt.subplots(1,3)
    x0=int(event[1])
    y0=int(event[2])
    t0=int(event[0])+int(DT/2)-pre_shift
    subarray=guv_tools.extract_subarray(frames_array, t0, x0, y0, DT, DX, DY)
    #sum:
    sumprojection_0=np.sum(subarray,axis=0)
    sumprojection_1=np.sum(subarray,axis=1)
    sumprojection_2=np.sum(subarray,axis=2)


    #show:
    ax[0].imshow(sumprojection_0, aspect=1)
    ax[0].set_title('SUM_event' + str(event_no).zfill(4))
    ax[0].set_xlabel("X-pos, pixels")
    ax[0].set_ylabel("Y-pos,pixels")
    ax[1].imshow(sumprojection_1, aspect='auto')
    ax[1].set_xlabel("X-pos, pixels")
    ax[1].set_ylabel("Time,frames")
    ax[2].imshow(sumprojection_2,aspect='auto')
    ax[2].set_xlabel("Y-pos, pixels")
    ax[2].set_ylabel("Time,frames")


    fig.tight_layout()
    fig.show()
    
    #final savings:
    #jpeg overview:
    kymo_overview_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_kymo.png")
    kymo_path= savepath/  kymo_overview_name
    fig.savefig(kymo_path)

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
    plt.close('all')


    







