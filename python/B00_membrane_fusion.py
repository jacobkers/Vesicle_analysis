import numpy as np
import cv2
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
    """Find the centers of white specks in the image."""
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
if 1: 
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
    filename ='MAX_2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
if 0:
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

with Image.open(image_path) as img:
    #gray_img = img.convert('L')
    img_array = np.array(img)

img_array=img_array-np.min(img_array)
maxim=np.max(img_array)

threshold=treshold_it(img_array)[0]

speck_centers = find_white_speck_centers(img_array,threshold=threshold)

print(f"Found {len(speck_centers)} white specks.")


fig, ax = plt.subplots()
#this is for consistent handling of axes:
x1=1
y1=0

for center in speck_centers:
    coords = circular_area_around(center[0], center[1], radius=4)
    vals = []
    for coord in coords:
        if 0 <= coord[x1] < img_array.shape[y1] and 0 <= coord[y1] < img_array.shape[x1]:
            vals.append(img_array[coord[x1], coord[y1]])  # Collect value
            img_array[coord[x1], coord[y1]] += 0.1*maxim  # Increment pixel value
fig, ax=plt.subplots(1,2)
ax[0].imshow(img_array, cmap='gray')
ax[0].set_title('Image with Circular Areas Around Specks')

for center in speck_centers:
    ax[0].plot(center[x1], center[y1], 'o', color='r')

#plt.show()

# Load TIFF movie
frame_number = 10  # Load the 11th frame (frame 10 is the 11th in zero-indexing)

# Load the frame
#frame = load_tiff_frame(movie_path, frame_number)
frames=load_tiff_movie(movie_path)

trace_data=np.zeros((len(frames),len(speck_centers)),dtype='float')
for fri, frame in enumerate(frames):
    print(fri)
    img_array = np.array(frame)
    for si,center in enumerate(speck_centers):
        coords = circular_area_around(center[0], center[1], radius=7)
        vals = []
        for coord in coords:
            if 0 <= coord[x1] < img_array.shape[y1] and 0 <= coord[y1] < img_array.shape[x1]:
                vals.append(img_array[coord[x1], coord[y1]])  # Collect value
                img_array[coord[x1], coord[y1]] += 0.1*maxim  # Increment pixel value
        trace_data[fri,si]=np.sum(vals)
    # Display the frame using matplotlib
ax[1].plot(trace_data)
ax[1].set_title('traces')
fig.show()
dum=-1




