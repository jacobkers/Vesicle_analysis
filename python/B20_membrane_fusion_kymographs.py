import numpy as np
import cv2
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tf
import guv_tools


def load_tiff_frame(file_path, frame_index):
    # Open the TIFF file
    with tf.TiffFile(file_path) as tif:
        # Load a specific frame (zero-indexed)
        frame = tif.pages[frame_index].asarray()
    return frame

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

def circular_area_around(x=0, y=0, radius=25):
    """Generate coordinates for a circular area around a center point."""
    binary_image = np.zeros((2 * radius, 2 * radius), dtype=np.uint8)
    center = (radius, radius)
    cv2.circle(binary_image, center, radius, 255, -1)
    coords = np.argwhere(binary_image == 255)
    coords = coords - radius + [int(y), int(x)]
    return coords


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


#load movie:
frames=load_tiff_movie(movie_path)
frames_array=[]
for frame in frames:
   frames_array.append(np.array(frame))
frames_array=np.array(frames_array)


#load events
event_data_name=label +"_events" +  str(".csv")
csv_events=moviepath /  event_data_name
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
    projection_0=np.sum(subarray,axis=0)
    projection_1=np.sum(subarray,axis=1)
    projection_2=np.sum(subarray,axis=2)
    #show:
    ax[0].imshow(projection_0, aspect=1)
    ax[0].set_title('event' + str(event_no).zfill(4))
    ax[0].set_xlabel("X-pos, pixels")
    ax[0].set_ylabel("Y-pos,pixels")
    ax[1].imshow(projection_1, aspect='auto')
    ax[1].set_xlabel("X-pos, pixels")
    ax[1].set_ylabel("Time,frames")
    ax[2].imshow(projection_2,aspect='auto')
    ax[2].set_xlabel("Y-pos, pixels")
    ax[2].set_ylabel("Time,frames")
    fig.tight_layout()
    fig.show()
    
    #final savings:
    kymo_name = 'kymographs_' + label +'/' + 'event' + str(event_no).zfill(4) +  str("_kymo.png")
    kymo_path= moviepath/ kymo_name
    fig.savefig(kymo_path)
    dum=1
    plt.close()
plt.close('all')


    







