import numpy as np
import cv2
import csv
from os.path import normpath
from PIL import Image
from scipy import ndimage
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tf
import time


def load_tiff_frame(file_path, frame_index):
    # Open the TIFF file
    with tf.TiffFile(file_path) as tif:
        # Load a specific frame (zero-indexed)
        frame = tif.pages[frame_index].asarray()
    return frame

def treshold_it(im):
    """ treshold by triangulation, following Margreet Docter 
    JacobKerts, 2023"""
    rr,cc=im.shape
    # sort and scale on number of pixels (to equalize axes)
    impixels=im.flatten()
    impixels_sorted=np.sort(impixels)
    Npix=len(impixels)
    pix_ax=np.arange(0, Npix, 1)
    Ipix=np.max(impixels)
    impixels_sorted=impixels_sorted/Ipix*Npix

    #fit on lower half of N:
    lowerhalf_N=impixels_sorted[0:int(Npix/2)]
    lowerhalf_pix_ax=pix_ax[0:int(Npix/2)]
    lowerfit_p=np.polyfit(lowerhalf_pix_ax,lowerhalf_N,1)
    lowerfit=np.polyval(lowerfit_p, pix_ax)

    #fit on higher half of I:
    upperhalf_I=impixels_sorted[impixels_sorted>Npix/2]
    upperhalf_pix_ax=pix_ax[impixels_sorted>Npix/2]
    upperfit_p=np.polyfit(upperhalf_pix_ax,upperhalf_I,1)
    upperfit=np.polyval(upperfit_p, pix_ax)
    #get cross-point
    xc=(lowerfit_p[1]-upperfit_p[1])/(upperfit_p[0]-lowerfit_p[0])
    yc=np.polyval(lowerfit_p,xc)

    #get 'knee'
    #rr=np.hypot((1:length(sim))-xc).'.^2, (sim-yc).^2);
    rr=np.hypot(pix_ax-xc,impixels_sorted-yc)
    x_kn=pix_ax[(rr== min(rr))]
    y_kn=impixels_sorted[(rr== min(rr))]
    #scale value back
    treshold=y_kn/Npix*Ipix

    im_BW=(im>treshold)*1.0
    im_tres=(im>treshold)*im

    return treshold, im_tres, im_BW

def find_white_speck_centers(img_array, threshold=1, min_size=2):
    """Find the centers of white specks in an image image."""
    binary = img_array > threshold
    labeled, num_features = ndimage.label(binary)
    centers = ndimage.center_of_mass(binary, labeled, range(1, num_features + 1))
    
    sizes = ndimage.sum(binary, labeled, range(1, num_features + 1))
    mask = sizes >= min_size
    filtered_centers = [center for center, is_large_enough in zip(centers, mask) if is_large_enough]

    return filtered_centers

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
    label='short'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
if 1:
    label='long'
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
trace_data_name="collected_data_" + label + str(".csv")
csv_source=moviepath /  trace_data_name
csv_path_in = Path(csv_source)
trace_data=[]
print(csv_source.stem)

trace_data = np.loadtxt(csv_source, delimiter=';')


# plot traces
frs,N_events=np.shape(trace_data)

fig, ax=plt.subplots(2,2)
for trace in trace_data.T:
    dif_trace=np.diff(trace)
    mxi=np.argmax(dif_trace)

    start=np.max([mxi-50, 0])
    stop=np.min([mxi+50, frs])
    trace_cut=trace[start:stop]
    dif_trace_cut=dif_trace[start:stop]

    #show:
    if np.max(trace)>2E6:
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


    







