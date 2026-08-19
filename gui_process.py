#!/usr/bin/env python
# coding: utf-8

# # GUV Single Image Analysis Pipeline
# 
# This script contains a demo pipeline for analyzing GUV (Giant Unilamellar Vesicle) images. It single-frame data from .tif files.
# For movie-style analysis, we apply the same tools but in a more automated format, saving more intermediate material. Here, we collect a ll the basic steps.
# 
# Jacob Kers, 2024
# 
# ## Imports and Setup
import ast
import json
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from skimage import io
from skimage import measure
import numpy as np
from datetime import datetime
import tifffile

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

import guv_binary_ops, guv_tools

plt.rcParams['figure.figsize'] = [7, 5]

# ## Giant Unilamellar Vesicle or GUV
# Our basic 'info unit' is a single GUV, we note it as ROI (region-of-interest).
# We keep track of where it came from via a simple excel table, easily readable for both user and Python.
# The 'GUV' class closely follows the header in the Excel table.
# Here, we index per movie, then per ROI. For a single GUV or ROI, we define a 'GUV object'.

class GUV:
    def __init__(self):
        self.pathname = 0
        self.filename = 0
        self.exp_id = 0
        self.movie_id = 0
        self.guv_id = 0
        self.use_it = 0
        self.notes = 'any note'


def expand_df(df, pic_format='png'):

    # Read as DataFrame:
    #build a list of 'GUV' objects:
    Guv_list = []

    # flatten df: expand properties JSON
    props_df = df["properties_json"].apply(
        lambda x: json.loads(x) if x else {}
    ).apply(pd.Series)
    df_flat = pd.concat(
        [df.drop(columns=["properties_json"]),
         props_df],
        axis=1
    )
    # select the user-flagged ones:
    df_to_use=df_flat[df_flat['use_it'] == 1]
    for ix, guvrow in enumerate(df_to_use["id"]):
        Guv = GUV()
        row = df_to_use.iloc[ix]

        for col, val in row.items():
            if col.isidentifier():
                setattr(Guv, col, val)

        #transform for later use:
        Guv.work_weights = ast.literal_eval(Guv.work_weights)
        Guv_list.append(Guv)


    #set up parameters we are interested in. These parameters follow the structure and shape of the GUV movie
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
    all_resolution=[]  #resolution (pix per um)


    #Main:
    # pick a GUV and show its color channels and the 'work image', which is just the sum of these channels:
    for Guv in Guv_list:
        print('working: ', str(Guv.id), ':',Guv.experiment_label)
        image_path = Guv.pathname + '\\' + Guv.filename
        if pic_format != 'none':
            graphs_pathname = Guv.pathname + '\\' + 'graphs\\'
            if not Path(graphs_pathname).is_dir():
                Path(graphs_pathname).mkdir()

        #if filename contains a template:
        if  '*' in Guv.filename: #OR: assemble from more
            roi=[]
            guvpth=Path(Guv.pathname)
            for channelpath in guvpth.glob("**/*"+ Guv.filename):  # find all channel files in inpath
                roi.append(np.array(io.imread(channelpath)))
                # To get info:
                with tifffile.TiffFile(channelpath) as tif:
                    xres = tif.pages[0].tags["XResolution"].value
                    # xres is a tuple (numerator, denominator)
                    x_calibration = xres[0] / xres[1]
                    #print("resolution:", 100/x_calibration)

        else: #load from single file:
            roi = np.array(io.imread(image_path))
            # To get info:
            if Guv.pixel_size > 0:
                x_calibration = float(Guv.pixel_size)
            else:
                with tifffile.TiffFile(image_path) as tif:
                    xres = tif.pages[0].tags["XResolution"].value
                    # xres is a tuple (numerator, denominator)
                    x_calibration = xres[0] / xres[1]
                    #print("resolution:", 100/x_calibration)

        # handle single-channel images:
        if roi.ndim == 2:
            roi = np.expand_dims(roi, axis=0)

        clrs, rr,cc,=np.shape(roi)

        # setup a work image for edge detection etc, use a weight key for this
        for color_i, chan in enumerate(roi):
            if color_i==0:
                roi_work=Guv.work_weights[color_i]*(chan-np.min(chan))
            else:
                roi_work = roi_work + Guv.work_weights[color_i]*(chan - np.min(chan))
            if color_i== Guv.channel_of_interest:
                roi_main = chan  #to be used later, for illustration and so on

        # EXPORT GRAPHICS: ---------------------------------------------------------
        #set up, show and save work plot:
        if pic_format != 'none':
            fig, axs = plt.subplots(1, clrs +1)
            #note that we assume that a picture is a single image of one or more channels, "CXY"
            for color_i, chan in enumerate(roi):
                axs[color_i].imshow(chan)
                axs[color_i].set_title('channel'+str(color_i))
            axs[color_i+1].imshow(roi_work)
            axs[color_i+1].set_title('work image')
            fig.tight_layout()
            target = graphs_pathname + 'Guv_' + str(Guv.id).zfill(3) + '_1_separate_channels.' + pic_format
            fig.savefig(target, format=pic_format)
            plt.close('all')
        #---------------------------------------------------------------------------------------------


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
            if len(regprops) > 0:
                xm, ym = regprops[0].centroid

            #EXPORT GRAPHICS: build a figure showing the masks:-------------------------------------
            if pic_format != 'none':
                fig, axs = plt.subplots(2, 4)
                axs[0,0].imshow(roi_work)
                axs[0,0].set_title('1.work image')
                axs[0,1].imshow(mask_0)
                axs[0,1].set_title('2.tresholded')
                axs[0,2].imshow(mask_1)
                axs[0,2].set_title('3.filled')
                axs[0,3].imshow(mask_2)
                axs[0,3].set_title('4.cleaned')
                axs[1,0].imshow(mask_3)
                axs[1,0].set_title('5.eroded')
                axs[1,1].imshow(mask_4)
                axs[1,1].set_title('6.central object')
                axs[1,2].imshow(mask_5)
                axs[1,2].set_title('7.dilated')
                #if succesful, plot COM:
                if len(regprops)>0:
                    #because later we obtain a more precise measure of the avarge radius,
                    # here we revert to relative values for minor and major ax-radii:
                    axs[1,2].plot(ym,xm, 'ro', markersize=5)
                    axs[1,3].imshow(roi_work*mask_5)
                    axs[1,3].plot(ym,xm, 'ro', markersize=5)
                    axs[1,3].set_title('8.masked work image')
                fig.tight_layout()
                #plt.show()
                #save this figure
                target= graphs_pathname + 'Guv_'+ str(Guv.id).zfill(3) +'_2_masking.'+ pic_format
                fig.savefig(target, format=pic_format)
                plt.close('all')
            #-----------------------------------------------------------------------------

            if len(regprops) > 0:
                r_eq = regprops[0].equivalent_diameter_area / 2
                rmin_rel = regprops[0].axis_minor_length / 2 / r_eq
                rmaj_rel = regprops[0].axis_major_length / 2 / r_eq
                area_rel = regprops[0].area / (r_eq ** 2)
                perimeter_rel = regprops[0].perimeter / r_eq


            if len(regprops)>0:
                # build inner and outer masks (in cartesian coordiantes)
                ring_band=2*disk_sz
                inner_mask = guv_binary_ops.binary_erosion(mask_5, guv_binary_ops.disk(ring_band), iterations = 3)
                outer_mask = 1-guv_binary_ops.binary_dilation(mask_5, guv_binary_ops.disk(ring_band), iterations = 1)
                edge_mask=mask_5.astype(float) -inner_mask

                #we would like to do this for all rois:
                I_inner_mean=[]
                I_inner_median=[]
                I_outer_mean=[]
                I_outer_median=[]
                max_value=[]
                mean_value=[]
                radius_mean=[]
                N_colors=len(roi)
                for color_i, chan in enumerate(roi):
                    #get values from the inner - and outer area. By buffering into an area, we can apply outlier detection on a later stage
                    inner_pixels = chan[inner_mask.astype(bool)]
                    inner_pixels, outliers, flags = guv_tools.outlier_flag(inner_pixels, tolerance=3, sig_change=0.7, how=1, sho=0, demo=0)
                    I_inner_mean.append(guv_tools.safe_mean(inner_pixels))
                    I_inner_median.append(guv_tools.safe_median(inner_pixels))

                    outer_pixels=chan[outer_mask.astype(bool)]
                    outer_pixels, outliers, flags = guv_tools.outlier_flag(outer_pixels, tolerance=3, sig_change=0.7, how=1, sho=0, demo=0)
                    I_outer_mean.append(guv_tools.safe_mean(outer_pixels))
                    I_outer_median.append(guv_tools.safe_median(outer_pixels))

                    # # Radial mapping for edge:
                    # Now we have the center-of mass, we resample the pattern on a radial mesh
                    r_max=int(0.5*np.shape(roi_work)[0])
                    presets={#
                    'angularoversampling' : 0.7,
                    'radialoversampling' : 2,
                    'minradius' : 0,#the minimal radius is 0
                    'maxradius' : r_max
                    }
                    edge_map,QI, Xsamplinggrid, Ysamplinggrid=guv_tools.QI_map(edge_mask*chan, presets, xm, ym,demo=1)
                    inner_map=guv_tools.QI_map(inner_mask*chan, presets, xm, ym)
                    outer_map=guv_tools.QI_map(outer_mask*chan, presets, xm, ym)

                    #note that we use degrees and pixel units for plotting, not for sampling
                    rr,aa=edge_map.shape

                    # # Edge quantification
                    # We observe a somewhat sinusoid edge intensity variation, due to polarization effects. Here, we choose the maximum amplitude along the edge. We find it by mapping the maximum local intensity
                    # (note that we ignore its radial position) and remove the outliers first, then fit a sinusoid.
                    profile=np.nanmax(edge_map, axis=0)
                    profile_max=np.argmax(edge_map, axis=0)
                    if color_i== Guv.channel_of_interest:
                        resolution=(x_calibration)
                        radius_mean=(guv_tools.safe_mean(profile_max)/2)  #corrects for oversampling

                    # for a clean fit, we should remove the mean and remove the outliers ('buds')
                    x=np.arange(len(profile))
                    inliers, outliers, flags = guv_tools.outlier_flag(profile, tolerance=2, sig_change=0.9, how=1, sho=0, demo=0)
                    cln_x=x[np.nonzero(flags)]
                    cln_profile=profile[np.nonzero(flags)]

                    # Fit the sine wave
                    popt, pcov = guv_tools.fit_sine_to_trace(cln_x, cln_profile)
                    # Generate the fitted curve (on original x)
                    y_fit = guv_tools.sine_function(np.arange(len(x)), *popt)
                    max_value.append(np.max(y_fit))
                    mean_value.append(guv_tools.safe_mean(y_fit))

                    #EXPORT GRAPHICS: ---------------------------------------------------------
                    if pic_format != 'none':
                        if color_i== Guv.channel_of_interest:
                            #1) show and save the results for the main channel-of interests:
                            fig, axs = plt.subplots(1, 4)
                            axs[0].imshow(mask_5)
                            axs[0].set_title('work mask')
                            axs[1].imshow(inner_mask)
                            axs[1].set_title('inner mask')
                            axs[2].imshow(outer_mask)
                            axs[2].set_title('outer mask')
                            axs[3].imshow(edge_mask)
                            axs[3].set_title('edge mask')
                            fig.tight_layout()
                            target=graphs_pathname + 'Guv_' + str(Guv.id).zfill(3) +'_3_inner_outer_masks.'+ pic_format
                            fig.savefig(target, format=pic_format)
                            plt.close('all')

                            #2) radial mapping geometry:
                            skips=5
                            fig, axs = plt.subplots(1, 1)
                            axs.imshow(roi_main)
                            axs.plot(Ysamplinggrid[::skips,::skips], Xsamplinggrid[::skips,::skips], '-')
                            fig.tight_layout()
                            #save this figure
                            target=graphs_pathname + 'Guv_' + str(Guv.id).zfill(3) +'_4_radial_sampling.' + pic_format
                            fig.savefig(target, format=pic_format)
                            plt.close('all')
                            #plt.show()

                            #3) polar maps from the radial mapping:
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
                            target=graphs_pathname +  '/Guv_' + str(Guv.id).zfill(3) +'_5_radial_maps.' + pic_format
                            fig.savefig(target, format=pic_format)
                            plt.close('all')
                            #---------------------------------------------------------------------------

                            # 4) sine wave:-----------------------------------------------
                            fig, axs = plt.subplots(1,1)
                            axs.plot(x, profile, 'b-')
                            axs.plot(cln_x, cln_profile, 'k-')
                            axs.plot(cln_x, 0*cln_profile+max_value[color_i], 'r--')
                            axs.plot(cln_x, 0*cln_profile+mean_value[color_i], '--')
                            axs.plot(y_fit)
                            fig.tight_layout()
                            #save this figure
                            target=graphs_pathname +  '/Guv_' + str(Guv.id).zfill(3) +'_6_edge_fit.' + pic_format
                            fig.savefig(target, format=pic_format)
                            plt.close('all')
                            #--------------------------------------------------------------------------------

                if N_colors<3: #pad channels
                    for ii in range(3-N_colors):
                        #allocate (multi-chan lists):
                        I_inner_mean.append(float('nan'))
                        I_inner_median.append(float('nan'))
                        I_outer_mean.append(float('nan'))
                        I_outer_median.append(float('nan'))
                        # this edge value compares to that of an IamgeJ cross-section profile
                        max_value.append(float('nan'))
                        mean_value.append(float('nan'))


                #allocate (multi-chan lists):
                I_inner_mean_all.append(I_inner_mean)
                I_inner_median_all.append(I_inner_median)
                I_outer_mean_all.append(I_outer_mean)
                I_outer_median_all.append(I_outer_median)
                # this edge value compares to that of an ImageJ cross-section profile
                I_edge_max_all.append(max_value)
                I_edge_mean_all.append(mean_value)

                #only for main channel: geometry: (here we re-scale the earlier values from the binary mask:
                # to the more precise edge analysis result.):
                all_resolution.append(resolution)
                all_radius_minor.append(rmin_rel*radius_mean)
                all_radius_major.append(rmaj_rel*radius_mean)

                all_area.append(area_rel*(radius_mean**2))
                all_perimeter.append(perimeter_rel*radius_mean)
                all_radius_mean.append(radius_mean)

            else: #if nothing worked .....
                all_resolution.append(float('nan'))
                all_radius_mean.append(float('nan'))
                all_radius_minor.append(float('nan'))
                all_radius_major.append(float('nan'))
                all_area.append(float('nan'))
                all_perimeter.append(float('nan'))
                emptylist= [float('nan')] * 3
                I_edge_max_all.append(emptylist)
                I_edge_mean_all.append(emptylist)
                I_inner_mean_all.append(emptylist)
                I_inner_median_all.append(emptylist)
                I_outer_mean_all.append(emptylist)
                I_outer_median_all.append(emptylist)


    #add new data:
    #add geometry:
    df_to_use = df_to_use.copy()
    df_to_use['edge_radius_minor_pixels'] = all_radius_minor
    df_to_use['edge_radius_mean_pixels'] = all_radius_mean
    df_to_use['edge_radius_major_pixels'] = all_radius_major
    df_to_use['area_pixels_sq'] = all_area
    df_to_use['perimeter_pixels'] = all_perimeter
    df_to_use['pix_per_um'] = all_resolution
    #intensity per channel:
    for chan_i in range(N_colors):
        ch_str='Ch'+str(chan_i)+'_'
        df_to_use[ch_str+'edge_maximum'] = [item[chan_i] for item in I_edge_max_all]
        df_to_use[ch_str+'edge_mean'] = [item[chan_i] for item in I_edge_mean_all]
        df_to_use[ch_str+'inside_mean'] = [item[chan_i] for item in I_inner_mean_all]
        df_to_use[ch_str+'inside_median'] = [item[chan_i] for item in I_inner_median_all]
        df_to_use[ch_str+'outside_mean'] = [item[chan_i] for item in I_outer_mean_all]
        df_to_use[ch_str+'outside_median'] = [item[chan_i] for item in I_outer_median_all]
    return df_to_use
