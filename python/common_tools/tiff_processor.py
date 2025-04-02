import nd2reader
import nd2
import numpy as np
from skimage import io
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from guv_io import load_tiff_movie_as_array
import guv_tools

from scipy import ndimage

import numpy as np
from scipy import ndimage

def find_local_maxima_2d(image, sigma=1.0, min_distance=1, R0=3):
    """
    Find local maxima in a 2D image array after applying a Gaussian filter and compute local summed intensity.
    
    Parameters:
    - image: 2D numpy array
    - sigma: Standard deviation for Gaussian filter
    - min_distance: Minimum number of elements separating peaks
    - R0: Radial distance for summed intensity calculation
    
    Returns:
    - maxima: 2D numpy array of shape (N, 2) with coordinates (x, y) of local maxima
    - intensities: 1D numpy array of shape (N,) with summed intensities for each maximum
    """
    # Apply Gaussian filter to smooth the image
    smoothed = ndimage.gaussian_filter(image, sigma=sigma)
    
    # Find local maxima using a morphological approach
    neighborhood = ndimage.generate_binary_structure(2, 2)
    local_max = (smoothed == ndimage.maximum_filter(smoothed, footprint=neighborhood))
    
    # Label connected components of local maxima
    labeled, num_features = ndimage.label(local_max)
    maxima = [ndimage.maximum_position(smoothed, labeled, i) for i in range(1, num_features + 1)]
    
    # Remove invalid maxima and convert to numpy array
    maxima = np.array([(x, y) for x, y in maxima if x is not None and y is not None])
    
    return maxima
    """ intensities = []
    for x, y in maxima:
        # Create a circular mask for summing intensity within radius R0
        y_indices, x_indices = np.ogrid[:image.shape[0], :image.shape[1]]
        mask = (x_indices - y) ** 2 + (y_indices - x) ** 2 <= R0 ** 2
        
        summed_intensity = np.sum(image[mask])
        intensities.append(summed_intensity) """

def split_frames(frames, N):
    ff = len(frames)  # Total number of frames
    L = ff // N       # Length of each slot
    cutoff = L * N    # Number of frames to keep
    frames = frames[:cutoff]  # Trim extra frames
    slots = np.array_split(frames, N)  # Split into N parts

    return slots

def load_nd2_movie(input_path, channel_index):
    #loop: 'images' contains all colors and all frames
    with nd2reader.Nd2(str(input_path)) as images:
        # Change to the third channel (0-based indexing)
        num_frames = len(images)  # Total number of images in the stack
        num_channels = len(images.channels)  # Assuming 4 channels if not automatically detected
        # Select the proper channel 
        chan_images = [images[i] for i in range(channel_index, num_frames, num_channels)]
    
    # Convert to a NumPy array (optional, if needed for further processing)
    frames = np.array(chan_images)    
    return frames

def load_nd2_movie_try2(input_path, channel_index):
    with nd2.ND2File(input_path) as ndfile:
        data = ndfile.asarray()  # Load the full multi-dimensional dataset
    frames=data[:,channel_index,:,:]
    return frames

# Read the existing Excel file

data_source_path = Path('M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/002_fusion_charge/overview_data')
xls_source= '25_slbassay_bert.xlsx'
xls_source = data_source_path / xls_source
df = pd.read_excel(xls_source)
# Display the data read from the Excel file
print("Measured properties:")
for hdr in list(df.columns.values):
    print(hdr)
df = df[df['use_it'] == 1]


#one path:
""" moviepath=Path('M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/002_fusion_charge/002_LUV_to_SLB/25_01_14_/0_DOTAP')
movie_filename = '25_01_14_sample1_1_000.nd2'
movie_path =  moviepath/ movie_filename """

max_frames=80
channel_index = 1
counter=0
for mv_pth, movie_filename in zip(df['Location on drive'], df['filename']):
    counter=counter+1
    print(str(counter) + ':' + movie_filename)
    movie_path=Path(mv_pth.replace("\\", "/"))
    source= movie_path / movie_filename
    movie_path / movie_filename
    #path to find slots:
    targetname= 'tiff_exports_max' + str(max_frames) + 'frames'
    tiff_path = movie_path / targetname
    #get (list of) movie:

    slotnames = [f for f in tiff_path.iterdir() if movie_filename[:-4] in f.name and ".tif" in f.name]
    print(slotnames)
  
    N = len(slotnames) # Number of slots
    
    slot_triplet=[]
    
    for i in range(3):
        slot_triplet.append(load_tiff_movie_as_array(slotnames[i]))
    counter=1 #we start at second slot
    results = []
    while counter < N-2:
        slot=slot_triplet[1]

        first_im=slot[0]
        last_im=slot[-1]
        slot=slot-np.min(slot)

        mean_projection_1 = np.mean(slot_triplet[1], axis=0)
        max_projection_1 = np.max(slot_triplet[1], axis=0)
        std_projection_0 = np.std(slot_triplet[0], axis=0)  
        std_projection_1 = np.std(slot_triplet[1], axis=0)
        std_projection_2 = np.std(slot_triplet[2], axis=0)
        
        dif_st_02= (std_projection_2)-std_projection_0
        

        #normalize:
        #background:
        #mean_projection_1=mean_projection_1-np.min(mean_projection_1)
        #std_projection_1=std_projection_2-np.min(std_projection_2)

        #mean_projection_1=mean_projection_1/np.median(mean_projection_1)
        #max_projection_1=max_projection_1/np.median(max_projection_1)
        #std_projection_2_2=std_projection_2/np.median(std_projection_2)
        

        #get all action:
        mx_tres, mx_BW, treshold_mx = guv_tools.treshold_it(max_projection_1)
        
        #get all prolonged action:
        st_tres, st_BW, treshold_st = guv_tools.treshold_it(std_projection_1)
        
        action_peaks=find_local_maxima_2d(st_tres, sigma=1.0, min_distance=1)
 
        R0=5
        for x, y in action_peaks:
            
            # Create a circular mask for summing intensity within radius R0
            y_indices, x_indices = np.ogrid[:mx_tres.shape[0], :mx_tres.shape[1]]
            mask = (x_indices - y) ** 2 + (y_indices - x) ** 2 <= R0 ** 2
        
            #collect intensities
            #summed_mx = np.sum(max_projection_1[mask])
            summed_mx = np.sum(dif_st_02[mask])
            summed_st = np.sum(std_projection_1[mask])
            results.append((x, y, summed_mx, summed_st))
            
            #collect_example_traces?

        #shift the slots as 2-3-1, load next in last:
        next_slot_pointer=counter+2

        slot_triplet=slot_triplet[1:]
        slot_next=(load_tiff_movie_as_array(slotnames[next_slot_pointer]))
        slot_triplet.append(slot_next)
        counter=counter+1
        print(counter)
        dum=1
        
    results_ar = np.array(results)

    fig,ax=plt.subplots(2,3)
    ax[0,0].imshow(std_projection_0)
    ax[0,0].set_title('ST0')
    ax[0,1].imshow(std_projection_1)
    ax[0,1].set_title('ST1')
    ax[0,2].imshow(std_projection_2)
    ax[0,2].set_title('ST2')
    ax[1,0].imshow(dif_st_02)
    ax[1,0].set_title('dif02')
    ax[1,2].plot(results_ar[:,2], results_ar[:,3],'o', markersize=2)
    ax[1,2].set_xlabel('dif_st13 (n.u)')
    ax[1,2].set_ylabel('std (n.u.)')
    ax[1,2].set_title('plt')
    
    fig.show()
    dum=1

        


