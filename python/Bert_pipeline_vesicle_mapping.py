#!/usr/bin/env python
# coding: utf-8

# # GUV Image Analysis Pipeline
# 
# This notebook contains a demo pipeline for analyzing GUV (Giant Unilamellar Vesicle) images. It single-frame data from .tif files.
# For movie-style analysis, we apply the same tools but in a more automated format, saving more intermediate material. Here, we collect a ll the basic steps.
# 
# Jacob Kers, 2024
# 
# ## Imports and Setup

import csv
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from skimage import measure



#set up local and import common tools
#customs:
import sys
import os
# Get the current working directory
current_directory = os.getcwd()
# Move one or two directories up
two_levels_up = os.path.abspath(os.path.join(current_directory, "..", ".."))
one_level_up = os.path.abspath(os.path.join(current_directory, ".."))
# Insert the path to sys.path
sys.path.insert(0, one_level_up)
sys.path.insert(0, two_levels_up)

from common_tools import guv_binary_ops
from common_tools import guv_tools


# set up autoreload on all files
#get_ipython().run_line_magic('load_ext', 'autoreload')
#get_ipython().run_line_magic('autoreload', '2')

plt.rcParams['figure.figsize'] = [7, 5]


# ## Giant Unilamellar Vesicle or GUV
# Our basic 'info unit' is a single GUV, we note it as ROI (region-of-interest).  We keep track of where it came from via a simple excel table, easily readable for both user and Python. The 'GUV' class closely follows the header in the Excel table. Here, we index per movie, then per ROI. For a single GUV or ROI, we define a 'GUV object'.
# 

class GUV:
    def __init__(self):
        self.pathname = 0
        self.filename = 0
        self.exp_id = 0
        self.movie_id = 0
        self.guv_id = 0
        self.use_it = 0
        self.notes = 'any note'


# # Collect info
# read GUV info from an Excel file and returns a list of GUV objects for a specific run ID.
# We define a `GUV` class to store properties of a single GUV movie.

outdir_test='M:/tnw/bn/cd/Shared/Jacob/TESTdata_out/2024_Bert/2025_04_23 vesicle_tests/'

# Example usages 
excelpath=Path("M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/005_analysis")
excelname =str("Bert_data_overview_test.xlsx")
targetname=str("Bert_data_results.xlsx")

# Read as DataFrame:
df = pd.read_excel(excelpath  / excelname)

# Display the data read from the Excel file
#print("Original Data:")
#print(df)

#build a list of 'GUV' objects:
#pathname	experiment_label	filename	exp_id	movie_id	guv_id	use_it	index
Guv_list = []
df_to_use=df[df['use_it'] == 1]
for ix, guvrow in enumerate(df_to_use["index"]):
    Guv = GUV()
    Guv.global_index = df_to_use.iloc[ix]["index"]
    Guv.pathname=df_to_use.iloc[ix]["pathname"]
    Guv.exp_label=df_to_use.iloc[ix]["experiment_label"]
    Guv.filename = df_to_use.iloc[ix]["filename"]
    Guv.exp_id = df_to_use.iloc[ix]["exp_id"]
    Guv.movie_id = df_to_use.iloc[ix]["movie_id"]
    Guv.guv_id = df_to_use.iloc[ix]["guv_id"]
    Guv.use_it=df_to_use.iloc[ix]["use_it"]
    Guv.notes = df_to_use.iloc[ix]["notes"]
    print('fetched: ', Guv.global_index, ':',Guv.exp_label)
    Guv_list.append(Guv)
    

#set up parameters we are interested in:
#intensity:
I_edge_max_all=[]    #maximum intensity value of the sinusoid fitting of radial-mapped the edge intensity (excluding buds)
I_edge_mean_all =[]  # same, mean value
I_inner_mean_all = []  #analog for inner area (based on the cartesian masks)         
I_inner_median_all =[]
I_outer_mean_all = []           
I_outer_median_all =[]

#geometry:
all_radius_mean =[] # mean radius of object (via radial maps)
all_radius_minor =[] # minor axis of object (via cartesian mask)
all_radius_major =[] # major axis of object (via cartesian mask)
all_area =[] #area of object
all_perimeter = [] # perimeter of object



#Main:
# pick a GUV and show its color channels and the 'work image', which is just the sum of these channels:
for Guv in Guv_list:
    print('working: ', Guv.global_index, ':',Guv.exp_label)
    image_path = Guv.pathname + '\\' + Guv.filename
    roi = np.array(io.imread(image_path))
    # extract other basic metadata
    clrs, rr,cc,=np.shape(roi)

    #set up, show and save work plot:
    fig, axs = plt.subplots(1, clrs +1)
    #setup a work image for edge detection etc
    for color_i, chan in enumerate(roi):
        if color_i==0: 
            roi_work=chan-np.min(chan)
        else:
                roi_work=+ chan - np.min(chan)
                roi_main = chan  #to be used later
        axs[color_i].imshow(chan)
        axs[color_i].set_title('channel'+str(color_i)) 

    #plot 
    axs[color_i+1].imshow(roi_work)
    axs[color_i+1].set_title('work image') 
    fig.tight_layout()
    #plt.show()
    #save
    fig.savefig(outdir_test + 'Guv' + str(Guv.global_index).zfill(3) +'_1_separate_channels.png')
    plt.close('all')
             
    #Isolate a GUV
    #set the scale of erosion /dilation
    disk_sz=int(0.02*np.shape(roi_work)[0])

    if np.max(np.array(roi_work))>0:
        roi_work=guv_tools.soft_mask_it(roi_work)
        roi_work=guv_tools.smooth_it(roi_work,labda=4)
        roi_work= roi_work.astype(int)
        
        #transfer to binary operations to gat masks and robust coordinates
        mask_0=guv_binary_ops.sorted_pixels_treshold(roi_work)[1]
        mask_1 = guv_binary_ops.binary_fill_holes(mask_0, guv_binary_ops.disk(disk_sz))
        mask_2 = guv_binary_ops.binary_opening(mask_1, guv_binary_ops.disk(disk_sz), iterations = 6)
        mask_3 = guv_binary_ops.binary_erosion(mask_2, guv_binary_ops.disk(disk_sz), iterations = 5)
        mask_4 = guv_binary_ops.mask_central_object(mask_3)[0]
        mask_5 = guv_binary_ops.binary_dilation(mask_4, guv_binary_ops.disk(disk_sz), iterations = 5)
        
        #get some basic shape properties:
        labels, n_labels = measure.label(mask_5, return_num = True)
        regprops = measure.regionprops(labels)
        #show:
        fig, axs = plt.subplots(2, 4)
        axs[0,0].imshow(roi_work)
        axs[0,1].imshow(mask_0)
        axs[0,2].imshow(mask_1)
        axs[0,3].imshow(mask_2)
        axs[1,0].imshow(mask_3)
        axs[1,1].imshow(mask_4)
        axs[1,2].imshow(mask_5)
        #if succesful, plot COM:
        if len(regprops)>0:
            xm,ym = regprops[0].centroid
            #because later we obtain a more precise measure of the avarge radius, here we revert to relative values for minor and major ax-radii
            r_eq=regprops[0].equivalent_diameter/2
            rmin_rel=regprops[0].axis_minor_length/2/r_eq
            rmaj_rel=regprops[0].axis_major_length/2/r_eq
            area=regprops[0].area
            perimeter= regprops[0].perimeter      

            axs[1,2].plot(ym,xm, 'ro', markersize=5)
            axs[1,3].imshow(roi_work*mask_5)
            axs[1,3].plot(ym,xm, 'ro', markersize=5)
        fig.tight_layout()
        #plt.show()
        #save this figure
        target='M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/misc/output_figs/Guv_no' + str(Guv.global_index).zfill(3) +'_2_masking.png'
        fig.savefig(target)
        plt.close('all')
        
        if len(regprops)>0:
            # build inner and outer masks (in cartesian coordiantes)
            inner_mask = guv_binary_ops.binary_erosion(mask_5, guv_binary_ops.disk(disk_sz), iterations = 3)                 
            outer_mask = 1-guv_binary_ops.binary_dilation(mask_5, guv_binary_ops.disk(disk_sz), iterations = 1)
            edge_mask=mask_5.astype(float) -inner_mask
            
            #get values from the inner - and outer area. By buffering into an area, we can apply outlier detection on a later stage
            inner_pixels = roi_main[inner_mask.astype(bool)]
            I_inner_mean=np.mean(inner_pixels)
            I_inner_median=np.median(inner_pixels)  
            outer_pixels=roi_main[outer_mask.astype(bool)]
            I_outer_mean=np.mean(outer_pixels)
            I_outer_median=np.median(outer_pixels)
            
            #allocate:
            I_inner_mean_all.append(I_inner_mean)       
            I_inner_median_all.append(I_inner_median)
            I_outer_mean_all.append(I_outer_mean)       
            I_outer_median_all.append(I_outer_median)

            # # Radial mapping
            # Now we have the center-of mass, we resample the pattern on a radial mesh
            r_max=int(0.5*np.shape(roi_work)[0])
            presets={#
            'angularoversampling' : 0.7, 
            'radialoversampling' : 2,
            'minradius' : 0,#the minimal radius is 0
            'maxradius' : r_max
            }
            edge_map,QI, Xsamplinggrid, Ysamplinggrid=guv_tools.QI_map(edge_mask*roi_main, presets, xm, ym,demo=1)
            inner_map=guv_tools.QI_map(inner_mask*roi_main, presets, xm, ym)
            outer_map=guv_tools.QI_map(outer_mask*roi_main, presets, xm, ym)
            
            #show and save:
            fig, axs = plt.subplots(1, 4)
            axs[0].imshow(mask_5)
            axs[1].imshow(inner_mask)
            axs[2].imshow(outer_mask)
            axs[3].imshow(edge_mask)
            fig.tight_layout()
            
            #plt.show()
            #save this figure
            target='M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/misc/output_figs/Guv_no' + str(Guv.global_index).zfill(3) +'_3_inner_outer_masks.png'
            fig.savefig(target)
            plt.close('all')
            
            #show and save:
            skips=5
            fig, axs = plt.subplots(1, 1)
            axs.imshow(roi_main)
            axs.plot(Ysamplinggrid[::skips,::skips], Xsamplinggrid[::skips,::skips], '-')
            fig.tight_layout()
            #save this figure
            target='M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/misc/output_figs/Guv_no' + str(Guv.global_index).zfill(3) +'_4_radial_sampling.png'
            fig.savefig(target)
            plt.close('all')
            #plt.show()
            #show:
            #note that we use degrees and pixel units for plotting, not for sampling
            rr,aa=edge_map.shape
            fig, axs = plt.subplots(1, 3)
            axs[0].imshow(inner_map,extent=[0,360,r_max,0], aspect='auto')
            axs[0].set_title('inner')
            axs[0].set_xlabel('angle')
            axs[1].imshow(outer_map,extent=[0,360,r_max,0], aspect='auto')
            axs[1].set_title('outer')
            axs[1].set_xlabel('angle')
            axs[2].imshow(edge_map,extent=[0,360,r_max,0], aspect='auto')
            axs[2].set_title('edge')
            axs[2].set_xlabel('angle')

            fig.tight_layout()
            #plt.show()
            #save this figure
            target='M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/misc/output_figs/Guv_no' + str(Guv.global_index).zfill(3) +'_5_radial_maps.png'
            fig.savefig(target)
            plt.close('all')

            # # Edge quantification
            # We observe a somewhat sinusoid edge intensity variation, due to polarization effects. Here, we choose the maximum amplitude along the edge. We find it by mapping the maximum local intensity 
            # (note that we ignore its radial position) and remove the outliers first, then fit a sinusoid.
            profile=np.nanmax(edge_map, axis=0)
            profile_max=np.argmax(edge_map, axis=0)
            radius_mean=np.nanmean(profile_max)/2  #corrects for oversampling
            #here we re-scale the earlier major and minor axis values:
            all_radius_minor.append(rmin_rel*radius_mean)
            all_radius_major.append(rmaj_rel*radius_mean)
            all_area.append(area)
            all_perimeter.append(perimeter)


            # for a clean fit, we should remove the mean and remove the outliers ('buds')
            x=np.arange(len(profile))
            inliers, outliers, flags = guv_tools.outlier_flag(profile, tolerance=2, sig_change=0.9, how=1, sho=0, demo=0)
            cln_x=x[np.nonzero(flags)]
            cln_profile=profile[np.nonzero(flags)]

            # Fit the sine wave
            popt, pcov = guv_tools.fit_sine_to_trace(cln_x, cln_profile)   

            # Generate the fitted curve (on original x)
            y_fit = guv_tools.sine_function(np.arange(len(x)), *popt)
            max_value=np.max(y_fit)
            mean_value=np.mean(y_fit)

            # this edge value compares to that of an IamgeJ cross-section profile
            I_edge_max_all.append(max_value) 
            I_edge_mean_all.append(mean_value) 
            all_radius_mean.append(radius_mean) 

            

            # show:
            fig, axs = plt.subplots(1,1)
            axs.plot(x, profile, 'b-')
            axs.plot(cln_x, cln_profile, 'k-')
            axs.plot(cln_x, 0*cln_profile+max_value, 'r--')
            axs.plot(cln_x, 0*cln_profile+mean_value, '--')
            axs.plot(y_fit)
            fig.tight_layout()
            #plt.show()
            #save this figure
            target='M:/tnw/bn/cd/Shared/Bert/002_liposome_fusion/misc/output_figs/Guv_no' + str(Guv.global_index).zfill(3) +'_6_edge_fit.png'
            fig.savefig(target)
            plt.close('all')
        else: #if nothing worked .....           
            all_radius_mean.append(float('nan')) 
            all_radius_minor.append(float('nan')) 
            all_radius_major.append(float('nan')) 
            all_area.append(float('nan')) 
            all_perimeter.append(float('nan')) 
            
            I_edge_max_all.append(float('nan')) 
            I_edge_mean_all.append(float('nan')) 
            I_inner_mean_all.append(float('nan'))       
            I_inner_median_all.append(float('nan'))
            I_outer_mean_all.append(float('nan'))       
            I_outer_median_all.append(float('nan'))


#add new data:
#intensity:
df_to_use['edge maximum'] = I_edge_max_all  
df_to_use['edge mean'] = I_edge_mean_all 
df_to_use['inside mean'] = I_inner_mean_all
df_to_use['inside median'] = I_inner_median_all
df_to_use['outside mean'] = I_outer_mean_all
df_to_use['outside median'] = I_outer_median_all

#geometry:
df_to_use['edge radius minor'] = all_radius_minor
df_to_use['edge radius mean'] = all_radius_mean  
df_to_use['edge radius major'] = all_radius_major
df_to_use['area'] = all_area
df_to_use['perimeter'] = all_perimeter



df_to_use.to_excel(excelpath  / targetname, index=False)
print(f"\nUpdated data has been written to target")

