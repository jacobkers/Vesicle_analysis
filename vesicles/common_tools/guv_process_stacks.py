""" vesicle data input-output
Jacob Kers 2024

 """
import time as tm
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import io
from vesicles.common_tools import guv_tools
from vesicles.common_tools import guv_binary_ops
from vesicles.common_tools import guv_io
import cv2
import csv
from scipy.ndimage import binary_opening, binary_closing, binary_fill_holes, binary_dilation, binary_erosion
from skimage.morphology import ball, disk, square, diamond, ball


def a20a_build_coordinates(im_ori_name,initval):
    """
    description: collect relevant coordinates (such as guv center) from tiff stacks and save as csv

    approach: a 'work stack' is created by just adding up all color channels

    #Jacob 2024 """
    #set paths:
    datapath_out_name = initval.mainpath_out + initval.subdir 
    in_path_name_rois = initval.mainpath_out + initval.subdir +str("/A10_rois")
    outpath_masks_name = initval.mainpath_out + initval.subdir +str("/A20a_masks")
    out_path_name = initval.mainpath_out + initval.subdir +str("/A20a_tracked/")
    roipath = Path(in_path_name_rois)
    maskpath=Path(outpath_masks_name)
    overviewpath = Path(out_path_name)
    if not overviewpath.is_dir():
        overviewpath.mkdir()
    
    if not maskpath.is_dir():
        maskpath.mkdir()
    
    fig, axs = plt.subplots(1, 3)
    #
    source = initval.mainpath_out + initval.subdir + im_ori_name + initval.nc_name
    ds_guvs = xr.load_dataset(source)
    xg=ds_guvs["X0"]
    yg = ds_guvs["Y0"]
    rg= ds_guvs["R0"]
    # set up 2D maps (guv, plane):
    all_guvs_okay_fr =[]
    all_guvs_xg = []
    all_guvs_yg = []
    all_guvs_R_minor = []
    all_guvs_R_major = []
    all_guvs_areas = []
    all_guvs_perimeters = []
    all_guvs_roundness = []
    all_guvs_std = []
    all_guvs_focalplane=[]

    for roi_i, x in enumerate(xg):  #work each GUV and its center coordinates:
        if initval.movie_id==-1 or roi_i==initval.movie_id:
        #1) load tracking channels and add them up in one stack-to-track:
            for ci, color_i in enumerate(initval.tracking_key):
                roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
                if ci==0:
                    roi_stack=io.imread(roipath / f"{roiname}")
                else:
                    roi_stack=roi_stack + io.imread(roipath / f"{roiname}")
        #2) obtain basic area properties from this tracking image:
            if roi_stack.ndim == 2: roi_stack = roi_stack[np.newaxis,:] # expand to third dimension
            #set up:
            all_xg=[];     all_yg=[];          all_R_minor=[];  all_R_major=[]
            all_areas=[];  all_perimeters=[];  all_roundness=[]; all_ok_frame =[]
            all_std=[]
            mask_stack=0*roi_stack
            roi_shp=np.shape(roi_stack)
            n_frames=roi_shp[0]
            for fri in np.arange(n_frames):
                good_guv_fr = True
                roi=roi_stack[fri,:,:]
                if fri==0:
                    roi0=roi
                #A. build an image that allows robust tracking
                # smooth, threshold:
                roi_tr=roi-np.min(roi)
                roi_tr = guv_tools.soft_mask_it(roi_tr)
                roi_tr = guv_tools.smooth_it(roi_tr, labda=2)
                roi_tr = roi_tr.astype(int)
                if np.ptp(roi_tr) < 1e-6:
                    good_guv_fr = False
                    print('bad' + str(fri))
                if good_guv_fr:
                    msk, BW_edge, xm, ym, rmin, rmaj, area, perimeter, roundness = guv_binary_ops.work_binaries(roi_tr)
                    #collect geometry properties for this guv:
                    all_ok_frame.append(True)
                    all_xg.append(xm)
                    all_yg.append(ym)
                    all_R_minor.append(rmin)
                    all_R_major.append(rmaj)
                    all_areas.append(area)
                    all_perimeters.append(perimeter)
                    all_roundness.append(roundness)
                    all_std.append(np.std(roi_tr*msk))
                    #we build a separate mask stack, to be saved as tiff:
                    mask_stack[fri,:,:]=msk
                else:
                    all_ok_frame.append(False)
                    all_xg.append(0)
                    all_yg.append(0)
                    all_R_minor.append(0)
                    all_R_major.append(0)
                    all_areas.append(0)
                    all_perimeters.append(0)
                    all_roundness.append(0)
                    all_std.append(0)
                #build and save summary figure:
                titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
                if  fri==0:
                    #show track example:
                    #image
                    fig1, axs1=plt.subplots(2,2)
                    axs1[0,0].imshow(roi)
                    axs1[0,0].set_title('original')
                    axs1[0,0].plot(ym,xm,'ro')
                    print("a20a:" + titl + str("frame") + str(fri))
            #grow 2D data maps:
            all_guvs_okay_fr.append(all_ok_frame)
            all_guvs_xg.append(all_xg)
            all_guvs_yg.append(all_yg)
            all_guvs_R_minor.append(all_R_minor)
            all_guvs_R_major.append(all_R_major)
            all_guvs_areas.append(all_areas)
            all_guvs_perimeters.append(all_perimeters)
            all_guvs_roundness.append(all_roundness)
            all_guvs_std.append(all_std)
            #1D:
            focalplane=np.argmax(all_std)

            all_guvs_focalplane.append(focalplane)

            # set up some plotting
            frax=np.arange(len(all_roundness))
            roundness_plot=np.array(all_roundness)
            std_plot = np.array(all_std)
            R_minor_plot=np.array(all_R_minor)
            R_major_plot=np.array(all_R_major)
            areas_plot=np.array(all_areas)

            valid_idx=np.nonzero(np.array(all_roundness)>0)
            #main axes
            axs1[0,1].plot(frax[valid_idx], R_minor_plot[valid_idx],'ko-')
            axs1[0,1].plot(frax[valid_idx], R_major_plot[valid_idx],'ro-')
            axs1[0,1].set_ylabel('ax length')
            axs1[0,1].set_xlabel('frame no.')
            axs1[0,1].legend(['R_minor', 'R_major'],loc='best', fontsize='xx-small')

            axs1[1,0].plot(frax[valid_idx], areas_plot[valid_idx],'bo-')
            axs1[1,0].set_ylabel('area')
            axs1[1,0].set_xlabel('frame no.')

            axs1[1,1].plot(frax[valid_idx], std_plot[valid_idx],'ko-')
            axs1[1, 1].plot(frax[focalplane], std_plot[focalplane], 'ro-')
            axs1[1,1].set_ylabel('standard deviation')
            axs1[1,1].set_xlabel('frame no.')
            outfig_name = out_path_name  + titl + str("frame") + str(fri)+ str("_track_example.png")

            fig1.savefig(outfig_name)
            if roi_i==0:
                fig.show()
            plt.close()

            #save_mask:
            maskname= ("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(initval.tracking_key) + str("_BW.tif")
            io.imsave(maskpath / f"{maskname}", mask_stack, check_contrast=False)

            #save montage 1:
            fig, axs = plt.subplots(1, 1)
            mtg=guv_tools.make_montage(mask_stack, format_out='tiff')
            axs.imshow(mtg, cmap="gray", interpolation="nearest")
            mtg_plotname= titl + str("frame") + str(fri)+ str("_mask_example.png")
            fig.savefig(overviewpath / f"{(mtg_plotname)}", dpi=500)
            plt.close('all')

            #save montage 2:
            fig, axs = plt.subplots(1, 1)
            mtg=guv_tools.make_montage(roi_stack*mask_stack, format_out='tiff')
            axs.imshow(mtg, cmap="gray", interpolation="nearest")
            mtg_plotname= titl + str("frame") + str(fri)+ str("_work_im_example.png")
            fig.savefig(overviewpath / f"{(mtg_plotname)}", dpi=500)
            plt.close('all')


    # save same data to existing .nc with planes as second axis:
    save_geometry(all_guvs_xg,
                  all_guvs_yg,
                  all_guvs_R_minor,
                  all_guvs_R_major,
                  all_guvs_areas,
                  all_guvs_perimeters,
                  all_guvs_roundness,
                  all_guvs_std,
                  all_guvs_focalplane,
                  all_guvs_okay_fr,
                  source)


def analyze_edge_profile(profile, initval,fri):
    edge_value=np.nanmean(profile)
    #from imageJ inspection:
    # - angular sampling starts at the bottom (both in ImageJ and the python export pics)
    # - proceeds in CCW fashion
    # - the highest intensity (due to polarization effects) is visible on the horizontal, i.e. at Q1 ('right) and Q3('left')
    # - thus, we start at the lower end of a sine function that we want the amplitude from

    # - for a clean fit, we should remove the mean and remove the outliers ('buds')
    # Fit the sine wave
    x=np.arange(len(profile))
    inliers, outliers, flags = guv_tools.outlier_flag(profile, tolerance=2.5, sig_change=0.7, how=1, sho=0, demo=0)
    cln_x=x[np.nonzero(flags)]
    cln_profile=profile[np.nonzero(flags)]
    if len(cln_profile)>0:
        popt, pcov = guv_tools.fit_sine_to_trace(cln_x, cln_profile)   
        # Generate the fitted curve (on original x)
        y_fit = guv_tools.sine_function(np.arange(len(x)), *popt)
        edge_value=np.max(y_fit)

        if 0: # fri==25: #fri==0: #test
            fig, axs = plt.subplots(1,1)
            axs.plot(cln_x, cln_profile)
            axs.plot(y_fit)
            fig.tight_layout()
            fig.show()
            dum=1
            plt.close("all")
    else:
        edge_value=np.nan
    return edge_value        

def a20b_map_color_channels(im_ori_name,initval):
    """ collect values from various color channels
#Jacob 2024 """
    datapath_out_name = initval.mainpath_out + initval.subdir 
    in_path_name_rois = initval.mainpath_out + initval.subdir +str("/A10_rois")
    in_path_name_masks = initval.mainpath_out + initval.subdir +str("/A20a_masks")
    in_path_name_tracked = initval.mainpath_out + initval.subdir +str("/A20a_tracked/")
    out_path_name = initval.mainpath_out + initval.subdir +str("/A20b_processed/")
    roipath = Path(in_path_name_rois)
    maskpath= Path(in_path_name_masks)
    out_path = Path(out_path_name)
    if not out_path.is_dir(): out_path.mkdir()

    #load existing nc data
    source = initval.mainpath_out + initval.subdir + im_ori_name + initval.nc_name
    ds_guvs = xr.load_dataset(source)
    [n_guvs, n_planes]=np.shape(ds_guvs["Area"])
    xg = ds_guvs["X0"]

    n_col = initval.N_colors
    #set up the data containers(dims index, plane, color)
    all_guvs_inside_I = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_edge_I_mx = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_edge_I_sum_msk = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_edge_I_sum_pol = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_edge_I_sum_std = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_outside_I = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_LC = np.zeros((n_guvs, n_planes,n_col))
    all_guvs_LC_excess = np.zeros((n_guvs, n_planes,n_col))


    for guv_i, dum in enumerate(xg):  #work each GUV and its center coordinates:
        fig1, axs1=plt.subplots(2,initval.N_colors)
        for color_i in np.arange(initval.N_colors):
            #load tracking channel:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(guv_i) + str("_c")+str(color_i) + str(".tif")
            maskname=str("from_")+ im_ori_name + str("_roi")+str(guv_i) + str("_c")+str(initval.tracking_key) + str("_BW.tif")
            roi_stack=io.imread(roipath / f"{roiname}")
            if roi_stack.ndim == 2: roi_stack = roi_stack[np.newaxis,:] # expand to third dimension
            mask_stack=io.imread(maskpath / f"{maskname}")
            roi_shp=np.shape(roi_stack)

            if len(roi_shp)==2:
                n_frames=1
            if len(roi_shp)==3: #stack
                n_frames=roi_shp[0]
            all_inside_I=[]
            all_edge_I_mx=[]
            all_edge_I_sum_msk=[]
            all_edge_I_sum_pol=[]
            all_edge_I_sum_std=[]
            all_outside_I=[]
            all_LC=[]
            all_LC_excess=[]
            for fri in np.arange(n_frames):
                ok_fr = ds_guvs["Okayframe"].isel(index=guv_i, plane=fri).item()
                if ok_fr:
                    if len(roi_shp)==2:
                        roi=roi_stack
                    if len(roi_shp)==3: #stack
                        roi=roi_stack[fri,:,:]
                        all_mask=mask_stack[fri,:,:]
                        inner_mask = binary_erosion(all_mask, disk(3), iterations = 3)
                        blankcenter_mask= binary_erosion(all_mask, disk(3), iterations = 8)
                        edge_mask=all_mask-inner_mask
                        outer_mask = 1-binary_dilation(all_mask, disk(3), iterations = 3)
                        inner_donut_mask=inner_mask & ~blankcenter_mask

                    xm = ds_guvs["Xg"].isel(index=guv_i, plane=fri).item()
                    ym = ds_guvs["Yg"].isel(index=guv_i, plane=fri).item()
                    rm = ds_guvs["R_major"].isel(index=guv_i, plane=fri).item()

                    #B. use the track coordinates to force-edge_map the original image 
                    maxrad=2*rm
                    #perimeter_pixels_quart=np.ceil(2*np.pi*maxrad)/4
                    #angular_sampling_value=90/perimeter_pixels_quart
                    presets={#
                    'angularoversampling' : 0.7, 
                    'radialoversampling' : 2,
                    'minradius' : 0,#the minimal radius is 0
                    'maxradius' : 2*rm
                    }
                    edge_map=guv_tools.QI_map(edge_mask*roi, presets, xm, ym)
                    inner_map=guv_tools.QI_map(inner_mask*roi, presets, xm, ym)
                    outer_map=guv_tools.QI_map(outer_mask*roi, presets, xm, ym)

                    #analyze_map 
                    # 1) inside intensity, outside intensity
                    insides=(np.array(inner_map[np.nonzero(inner_map>0)]))
                    outsides=(np.array(outer_map[np.nonzero(outer_map>0)]))
                    if len(insides)>0: 
                        all_inside_I.append(np.mean(insides))
                        all_guvs_inside_I[guv_i,fri,color_i]=np.mean(insides)
                    else:
                        all_inside_I.append(0)
                    if len(outsides)>0: 
                        all_outside_I.append(np.mean(outsides))
                        all_guvs_outside_I[guv_i, fri, color_i] = np.mean(outsides)
                    else:
                        all_outside_I.append(0)
                    # 2) edge intensity (note we treat the edge differently:
 
                    if np.sum((np.shape(edge_map)))>0:
                        #a) maximum of peak
                        profile=np.nanmax(edge_map, axis=0)
                        edge_val=analyze_edge_profile(profile, initval,fri)
                        all_edge_I_mx.append(edge_val)
                        all_guvs_edge_I_mx[guv_i, fri, color_i] = edge_val
                        
                        #b1) sum of edge mask:
                        edge_mask_sum=np.sum(edge_mask*roi)
                        #b2) sampling-corrected sum of polar map
                        sum_profile=guv_tools.QI_map_analyze(edge_map, presets)
                        all_edge_I_sum_msk.append(edge_mask_sum)
                        all_guvs_edge_I_sum_msk[guv_i, fri, color_i] = edge_mask_sum
                        edge_pol_sum=np.nansum(sum_profile)
                        edge_pol_std=np.nanstd(sum_profile)                   
                        all_edge_I_sum_pol.append(edge_pol_sum)
                        all_guvs_edge_I_sum_pol[guv_i, fri, color_i] = edge_pol_sum
                        all_edge_I_sum_std.append(edge_pol_std)
                        all_guvs_edge_I_sum_std[guv_i, fri, color_i] = edge_pol_std
                        # 3) edge length from smoothened contour:
                        true_x, true_y = guv_tools.get_xy_contour(edge_map, presets)
                        LC, LR, RC=guv_tools.measure_perimeter(true_x, true_y)
                        all_guvs_LC[guv_i, fri, color_i] = LC
                        all_LC.append(LC)
                        all_LC_excess.append(LC/LR)
                        all_guvs_LC_excess[guv_i, fri, color_i] = LC/LR
                    else:
                        all_edge_I_mx.append(0)
                        all_edge_I_sum_msk.append(0)
                        all_edge_I_sum_pol.append(0)
                        all_edge_I_sum_std.append(0)
                        all_LC.append(0)
                        all_LC_excess.append(0)
                else:
                    all_inside_I.append(0)
                    all_edge_I_mx.append(0)
                    all_edge_I_sum_msk.append(0)
                    all_edge_I_sum_pol.append(0)
                    all_edge_I_sum_std.append(0)
                    all_outside_I.append(0)
                    all_LC.append(0)
                    all_LC_excess.append(0)

                #plotting
                titl = str("file_")+ im_ori_name  + str("_roi")+str(guv_i) +  str("c") + str(color_i)
                if  fri==0:
                    #show track example:
                    if initval.N_colors>1:
                        axs1[0,color_i].imshow(edge_map)
                        axs1[0,color_i].set_title(str("color") + str(color_i)) 
                    else:
                        axs1[0].imshow(edge_map)
                        axs1[0].set_title(str("color") + str(color_i)) 
                    print("a20b:" + titl + str("frame") + str(fri))
            #end results:
            if initval.N_colors>1:
                axs1[1,color_i].legend(['edge'],loc='best', fontsize='xx-small')
                axs1[1,color_i].plot(all_edge_I_mx,'ro', markersize=2)
                axs1[1,color_i].set_xlabel("frames")
            else:
                axs1[1].legend(['edge'],loc='best', fontsize='xx-small')
                axs1[1].plot(all_edge_I_mx,'ro', markersize=2)
                axs1[1].set_xlabel("frames")

            color_data=np.vstack((all_inside_I, 
                                  all_edge_I_mx,
                                  all_edge_I_sum_pol,
                                  all_edge_I_sum_std, 
                                  all_outside_I,
                                  all_LC,
                                  all_LC_excess))
            color_header=[str("color") + str(color_i)+str("_inside"), 
                          str("c") + str(color_i)+str("_edge_mx"),
                          str("c") + str(color_i)+str("_edge_sum"),
                          str("c") + str(color_i)+str("_edge_sum_std"),
                          str("c") + str(color_i)+str("_outside"),
                          str("c") + str(color_i)+str("_contour_L"),
                          str("c") + str(color_i)+str("_contour_ratio"),
                        ]
            


        dum=1
        #final savings:
        outfig_name = out_path_name  + titl + str("frame") + str(fri)+ str("_intensities.png")
        fig1.savefig(outfig_name)
        plt.close()
        
        # #csv:
        # csv_target=out_path_name  +str("file_")+ im_ori_name  + str("_roi")+str(guv_i) + "_all_data.csv"
        # with open(csv_target, "w",newline='') as csv_h:  # will overwrite existing
        #     # create the csv writer
        #     writer = csv.writer(csv_h, delimiter=";")
        #     writer.writerow(header_out)
        # csv_h.close()
        # tm.sleep(2)
        # #save results per GUV as csv
        # for row in np.transpose(data_out):
        #     with open(csv_target, "a",newline='') as csv_hi:
        #         # create the csv writer
        #         writer = csv.writer(csv_hi, delimiter=";")
        #         writer.writerow(row)
        # csv_hi.close()

    #nc, all guvs:
    save_colors(all_guvs_inside_I,
                all_guvs_edge_I_mx,
                all_guvs_edge_I_sum_msk,
                all_guvs_edge_I_sum_pol,
                all_guvs_edge_I_sum_std,
                all_guvs_outside_I,
                all_guvs_LC,
                all_guvs_LC_excess, source)


def show_roi_overviews(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to processed standardized tif roi-stacks from  format
    #Jacob 2024 """
    datapath_out_name = initval.mainpath_out + initval.subdir 
    in_path_name_rois = initval.mainpath_out + initval.subdir +str("/A10_rois")
    out_path_name = initval.mainpath_out + initval.subdir +str("/A20a_overviews/")
    roipath = Path(in_path_name_rois)
    overviewpath = Path(out_path_name)
    if not overviewpath.is_dir():
        overviewpath.mkdir()
    fig, axs = plt.subplots(1, 3)

    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        for color_i in np.arange(3):
            #load:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            roi_stack=io.imread(roipath / f"{roiname}")
            roi_shp=np.shape(roi_stack)
            if len(roi_shp)==3: #work stack
                roi0=roi_stack[0,:,:] 
                #walk frames [empty]:
                for roi in roi_stack:
                    dum=1
                    #process the work image
            else:
                roi0=roi_stack #single image
            roi0=roi0-np.min(roi0)
            #show the color channel
            fig, axs = plt.subplots(1,1)
            axs.imshow(roi0)
            titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i) + str("frame") + str(0)
            axs.set_title(titl) 
            outfig_name = out_path_name  + titl + str(".png")
            fig.savefig(outfig_name)
            plt.close()

def save_geometry(all_guvs_xg,
                  all_guvs_yg,
                  all_guvs_R_minor,
                  all_guvs_R_major,
                  all_guvs_areas,
                  all_guvs_perimeters,
                  all_guvs_roundness,
                  all_guvs_std,
                  all_guvs_focalplane,
                  all_guvs_okay_fr,
                  source):
    n_guvs, n_planes = np.shape(all_guvs_xg)
    XGuvs = xr.load_dataset(source)
    xg_da = xr.DataArray(all_guvs_xg, dims=("index", "plane"),
                         coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Xg")
    yg_da = xr.DataArray(all_guvs_yg, dims=("index", "plane"),
                         coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Yg")
    R_minor_da = xr.DataArray(all_guvs_R_minor, dims=("index", "plane"),
                              coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="R_minor")
    R_major_da = xr.DataArray(all_guvs_R_major, dims=("index", "plane"),
                              coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="R_major")
    area_da = xr.DataArray(all_guvs_areas, dims=("index", "plane"),
                           coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Area")
    perimeters_da = xr.DataArray(all_guvs_perimeters, dims=("index", "plane"),
                                 coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Perimeter")
    roundness_da = xr.DataArray(all_guvs_roundness, dims=("index", "plane"),
                                coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Roundness")
    std_da = xr.DataArray(all_guvs_std, dims=("index", "plane"),
                                coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Standard_Deviation")
    focal_plane_da= xr.DataArray(all_guvs_focalplane, dims=("index"),
                          coords={"index": np.arange(n_guvs)}, name="focal_plane")

    okayframe_da = xr.DataArray(all_guvs_okay_fr, dims=("index", "plane"),
                                coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes)}, name="Okayframe")

    XGuvs = xr.merge([area_da, xg_da, yg_da, R_minor_da, R_major_da, perimeters_da, roundness_da, std_da, focal_plane_da, okayframe_da,XGuvs],compat='override')
    XGuvs.to_netcdf(source, mode="w")
    print(XGuvs)

def save_colors(all_guvs_inside_I,
                all_guvs_edge_I_mx,
                all_guvs_edge_I_sum_msk,
                all_guvs_edge_I_sum_pol,
                all_guvs_edge_I_sum_std,
                all_guvs_outside_I,
                all_guvs_LC,
                all_guvs_LC_excess, source):
    n_guvs, n_planes, n_colors = np.shape(all_guvs_inside_I)
    XGuvs = xr.load_dataset(source)
    inside_I_da = xr.DataArray(all_guvs_inside_I, dims=("index", "plane", "channel"),
                         coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                 "channel": np.arange(n_colors)}, name="Inside_I")
    outside_I_da = xr.DataArray(all_guvs_outside_I, dims=("index", "plane", "channel"), name="Outside_I")
    edge_I_mx_da = xr.DataArray(all_guvs_edge_I_mx, dims=("index", "plane", "channel"), name="edge_I_mx")
    edge_I_sum_msk_da = xr.DataArray(all_guvs_edge_I_sum_msk, dims=("index", "plane", "channel"),
                                  coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                          "channel": np.arange(n_colors)}, name="Edge_I_sum_msk")
    edge_I_sum_pol_da = xr.DataArray(all_guvs_edge_I_sum_pol, dims=("index", "plane", "channel"),
                                     coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                             "channel": np.arange(n_colors)}, name="Edge_I_sum_pol")
    edge_I_sum_std_da = xr.DataArray(all_guvs_edge_I_sum_std, dims=("index", "plane", "channel"),
                                     coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                             "channel": np.arange(n_colors)}, name="Edge_I_sum_std")
    all_guvs_LC_da = xr.DataArray(all_guvs_LC, dims=("index", "plane", "channel"),
                                     coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                             "channel": np.arange(n_colors)}, name="Edge_LC")
    all_guvs_LC_excess_da = xr.DataArray(all_guvs_LC_excess, dims=("index", "plane", "channel"),
                                     coords={"index": np.arange(n_guvs), "plane": np.arange(n_planes),
                                             "channel": np.arange(n_colors)}, name="Edge_LC_excess")

    XGuvs = xr.merge([inside_I_da, outside_I_da, edge_I_mx_da, edge_I_sum_msk_da, edge_I_sum_pol_da,
                    edge_I_sum_std_da,all_guvs_LC_da, all_guvs_LC_excess_da,XGuvs],compat='override')
    XGuvs.to_netcdf(source, mode="w")
    print(XGuvs)