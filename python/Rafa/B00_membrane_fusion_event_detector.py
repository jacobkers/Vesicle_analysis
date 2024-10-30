import numpy as np
import cv2
import csv
from PIL import Image
from scipy import ndimage
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tf
import time
from common_tools import guv_tools


def load_tiff_frame(file_path, frame_index):
    # Open the TIFF file
    with tf.TiffFile(file_path) as tif:
        # Load a specific frame (zero-indexed)
        frame = tif.pages[frame_index].asarray()
    return frame

def find_white_speck_centers(img_array, threshold=2, min_size=1):
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
if 1: 
        label='2_TIRF_488_001_PCPG_Chol_small_short_B'
        moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
        savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
        movie_filename = '2_TIRF_488_001_PCPG_Chol_small_short_B.tif'
        filename ='STD_2_TIRF_488_001_PCPG_Chol_small_short_B.tif'
if 0: 
    label='2_TIRF_488_001_PCPG_Chol-1_small_short'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol-1_small_short.tif'
if 0:
    label='2_TIRF_488_001_PCPG_Chol_long'
    moviepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/2023_Rafa/2024_10_02 membrane fusion')
    savepath=Path('M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/2023_Rafa/2024_10_02 membrane fusion')
    #moviepath=Path('D:/jkerssemakers/CD_Data_in/2023_Rafa/2024_10_02 membrane fusion')
    movie_filename = '2_TIRF_488_001_PCPG_Chol.tif'
    filename ='STD_2_TIRF_488_001_PCPG_Chol.tif'


projection_image_path =  moviepath/ filename
movie_path =  moviepath/ movie_filename

with Image.open(projection_image_path) as img:
    projection_image_array = np.array(img)

projection_image_array=projection_image_array-np.min(projection_image_array)
maxim=np.max(projection_image_array)

threshold=3*guv_tools.treshold_it(projection_image_array)[2]

speck_centers = find_white_speck_centers(projection_image_array,threshold=threshold)

print(f"Found {len(speck_centers)} white specks.")


fig, ax = plt.subplots()
#this is for consistent handling of axes:
x1=1
y1=0

for center in speck_centers:
    coords = circular_area_around(center[0], center[1], radius=9)
    vals = []
    for coord in coords:
        if 0 <= coord[x1] < projection_image_array.shape[y1] and 0 <= coord[y1] < projection_image_array.shape[x1]:
            vals.append(projection_image_array[coord[x1], coord[y1]])  # Collect value
            projection_image_array[coord[x1], coord[y1]] += 0.1*maxim  # Increment pixel value
fig, ax=plt.subplots(1,2)
ax[0].imshow(projection_image_array, cmap='gray')
ax[0].set_title('Image with Circular Areas Around Specks')

for center in speck_centers:
    ax[0].plot(center[x1], center[y1], 'o', color='r')

plt.show()

# Load TIFF movie
# Load the frames
#frame_number = 10  # Load the 11th frame (frame 10 is the 11th in zero-indexing)
#frame = load_tiff_frame(movie_path, frame_number)
frames=load_tiff_movie(movie_path)
ff=len(frames)
N_events=len(speck_centers)

#build traces
trace_data=np.zeros((ff,N_events),dtype='float')
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
        
#find start points events:
frs,N_events=np.shape(trace_data)
fig, ax=plt.subplots(2,2)
event_data=np.zeros((N_events,4),dtype='int')
for ti, trace in enumerate(trace_data.T):
    dif_trace=np.diff(trace)
    t0=np.argmax(dif_trace)
    slope=int(dif_trace[t0])
    x0=int(speck_centers[ti][0])
    y0=int(speck_centers[ti][1])
    event_data[ti]=(t0,x0,y0, slope)

#save centers plus start time
event_data_name=label +'_events' + str(".csv")
csv_target_c=savepath /  event_data_name
with open(csv_target_c, "w",newline='') as csv_c:  # will overwrite existing
    # create the csv writer
    writer = csv.writer(csv_c, delimiter=";")
    #f = open("test.csv", "a")
    #writer.writerow(row.keys())
    for data_row in event_data:  
        # create the csv writer
        writer = csv.writer(csv_c, delimiter=";")
        #f = open("test.csv", "a")
        writer.writerow(data_row) 

#save traces
trace_data_name=label +"_traces" +  str(".csv")

csv_target=savepath /  trace_data_name
with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
    # create the csv writer
    writer = csv.writer(csv_f, delimiter=";")
    #f = open("test.csv", "a")
    #writer.writerow(row.keys())
    for data_row in trace_data:         
        # create the csv writer
        writer = csv.writer(csv_f, delimiter=";")
        #f = open("test.csv", "a")
        writer.writerow(data_row) 

    







