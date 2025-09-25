# # GUV Image Analysis Pipeline
# This notebook contains a pipeline for analyzing GUV (Giant Unilamellar Vesicle) images. It processes both single-frame and time-trace data from .tif files.
# (under construction)

import csv
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import vesicles as vs
""" from vesicles import A00_init

 """
from vesicles import A00_init
from vesicles import A10_muscope_crop
from vesicles import A20_process_rois
from vesicles import A30_collect_processed_rois
from vesicles.common_tools import guv_io


# ### GUV Class Definition
class GUV:
    def __init__(self):
        self.exp_id = 0
        self.label = 'any_label'
        self.comment = []
        self.use_it = []
        self.crop_it = []
        self.dt = 1

# ## Helper Functions
# 
# ### `get_data_selections(run_id)`
# 
# This function reads GUV data from an Excel file and returns a list of GUV objects for a specific run ID.
# We define a `GUV` class to store properties of a single GUV movie.


# ## Main Analysis Pipeline
# The main analysis is divided in a few main steps. For historical reasons, these are labeled A00, A10 ...etc. These lalbels are also used for the organization of saved data (pictures, tables) so that one can backtrack this data to the generating code
# ### A00: set up the experiment
# Fetch the experiment parameters: these are listed in 'A00_init and include paths, movienames etc.'.
# An experiment has a unique index.
# Since I keep some local copies, I added a decimal to this index
# to tell the code where to look (local or remote)
expi = 0.2  
    # 0.2: Charu's test data, C=1, decimal .2 refers to remote drive
    # 1.2: Charu's test data, C=2, decimal .2 refers to remote drive
movie_to_use_list = [0]  #should be identical to 'movie-id' list in excel
initval = A00_init.get_exps(expi)

# A10: Cropping
# With cropping, we cut out individual vesicles from the stack and save them to individual tiff files. We do this because this eases the follow-up analysis: each stack is assumed to contain only one full vesicle in the center, with approximately a constant coverage of the middle area of the ROI.
# This step requires the user to perform (easy) pre-selection in Fiji or ImageJ. Please read the README.txt for detailed info how to do that.
if 0: A10_muscope_crop.main(initval)
# NOTE: this step stores intermediates and therefore needs to be run only once
# A20: First processing of regions-of-interest (ROIs)
# In this step, we first isolate the area of the vesicle to obtain masks, but also some general geometry features such as radius, area and other shape characteristics. Next, we perfom detailed analysis of every color channel 
if 1: A20_process_rois.main(initval,0,1)
# NOTE: this step stores intermediates and therefore needs to be run only once


# pre_selection
# For time-trace or z-plane .tif files, we process the data and create visualizations. Since these movies can have some time slots-of-interest, we load an extra excel table that allows a user to crop dat a of processed movies (or discard them at all). Note that the 'movie-I' field should match the above movie-IDs.
import importlib
importlib.reload(guv_io)
selections_filename="data_overview_Charu.xlsx"
Guv_list = guv_io.get_data_selections(round(expi), selections_filename)


# II. Multi-frame Data Processing and Visualization

if 0:
    A30_collect_processed_rois.main(initval, Guv_list, movie_to_use_list)
    plt.show()

# This completes the GUV image analysis pipeline. The notebook processes both single-frame and time-trace .tif files, collecting data and creating visualizations for various GUV metrics.
