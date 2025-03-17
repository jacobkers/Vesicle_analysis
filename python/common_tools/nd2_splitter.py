import nd2reader
import nd2
import numpy as np
from pathlib import Path
import pandas as pd

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


#one path:
moviepath=Path('M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/002_fusion_charge/002_LUV_to_SLB/25_01_14_/0_DOTAP')
movie_filename = '25_01_14_sample1_1_000.nd2'
movie_path =  moviepath/ movie_filename

channel_index = 1
frames= load_nd2_movie_try2(movie_path, channel_index)

dum=1