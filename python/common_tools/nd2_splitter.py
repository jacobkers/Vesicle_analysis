import nd2reader
import nd2
import numpy as np
from skimage import io
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import tifffile

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

#one path:
""" moviepath=Path('M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/002_fusion_charge/002_LUV_to_SLB/25_01_14_/0_DOTAP')
movie_filename = '25_01_14_sample1_1_000.nd2'
movie_path =  moviepath/ movie_filename """

max_frames=200
channel_index = 1
counter=0
for mv_pth, movie_filename in zip(df['Location on drive'], df['filename']):
    counter=counter+1
    print(str(counter) + ':' + movie_filename)
    movie_path=Path(mv_pth.replace("\\", "/"))
    source= movie_path / movie_filename
    movie_path / movie_filename
    #save path:
    targetname= 'tiff_exports_max' + str(max_frames) + 'frames'
    tiff_path = movie_path / targetname
    if not tiff_path.is_dir():
                tiff_path.mkdir()
    #get movie:            
    frames= load_nd2_movie_try2(source, channel_index)
    
    ff, rr,cc =np.shape(frames)   
    N = int(np.ceil(ff/max_frames)) # Number of slots
    if N>1:
        slots = split_frames(frames, N)
        for slot_i, slot in enumerate(slots):
            slot_start=slot_i*max_frames
            slot_stop=slot_i*max_frames+max_frames-1
            first_im=slot[0]
            last_im=slot[-1]
            max_projection = np.max(slot, axis=0)
            std_projection = np.std(slot, axis=0)
            fig,ax=plt.subplots(2,2)
            ax[0,0].imshow(first_im)
            ax[0,0].set_title('first image')
            ax[0,1].imshow(last_im)
            ax[0,1].set_title('last image')
            ax[1,0].imshow(max_projection)
            ax[1,0].set_title('MAX')
            ax[1,1].imshow(std_projection)
            ax[1,1].set_title('STD')
            movie_filename_out = movie_filename[:-4] + '_C1' + '_section'+ str(slot_start) + '_' + str(slot_stop) + '.tif'
            fig.savefig(tiff_path / (movie_filename_out[:-4] + '_projections.png'))
            movie_filename_out = movie_filename[:-4] + '_C1' + '_section'+ str(slot_start) + '_' + str(slot_stop) + '.tif'
            io.imsave(tiff_path / f"{movie_filename_out}", slot, check_contrast=False)
    else:
        movie_filename_out = movie_filename[:-4] + '_C1' + '_full' + '.tif'
        io.imsave(tiff_path / f"{movie_filename_out}", frames, check_contrast=False)

