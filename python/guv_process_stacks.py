""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import io
import guv_tools
import guv_binary_ops
import guv_io
import cv2
import csv

def a20a_build_coordinates(im_ori_name,guv_xyr,initval):
    """ collect relevant coordinates (such as guv center) from tiff stacks and save as csv
#Jacob 2024 """
    #set apaths:
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

    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        color_i=initval.tracking_key
        #load tracking channel:
        roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
        roi_stack=io.imread(roipath / f"{roiname}")
        roi_shp=np.shape(roi_stack)
        if len(roi_shp)==2:
            n_frames=1
        if len(roi_shp)==3: #stack
            n_frames=roi_shp[0]
        all_xg=[]
        all_yg=[]
        all_R_minor=[]
        all_rmaj=[]
        #n_frames=1
        mask_stack=0*roi_stack
        for fri in np.arange(n_frames):
            if len(roi_shp)==2:
                roi=roi_stack
            if len(roi_shp)==3: #stack
                roi=roi_stack[fri,:,:]
            if fri==0:
                roi0=roi
            #A. build an image that allows robust tracking 
            # smooth, treshold:    
            roi_tr=roi-np.min(roi)
            if np.max(np.array(roi_tr))>0:
                roi_tr=guv_tools.smooth_it(roi_tr,labda=2)
                roi_tr= roi_tr.astype(int)
                #roi_tr= guv_tools.treshold_it(roi_tr)[0]
                #roi_tr=guv_tools.sobel_it(roi_tr)   
                #roi_tr=guv_tools.smooth_it(roi_tr,labda=1)
                #transfer to binary operations to gat masks and robust coordinates
                msk, BW_edge, xm, ym, rmin, rmaj = guv_binary_ops.work_binaries(roi_tr)                    
                all_xg.append(xm)
                all_yg.append(ym)
                all_R_minor.append(rmin) 
                all_rmaj.append(rmaj) 
                mask_stack[fri,:,:]=msk
            else:
                all_xg.append(0)
                all_yg.append(0)
                all_R_minor.append(0)
                all_rmaj.append(0) 



            #build and save summary figure:    
            titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
            if  fri==0:
                #show track example:
                fig1, axs1=plt.subplots(2,2)
                axs1[0,0].imshow(roi)
                axs1[0,0].set_title('original') 
                axs1[0,1].imshow(roi_tr)
                axs1[0,1].set_title('work_image')
                axs1[0,1].plot(ym,xm,'ro')
                axs1[1,0].imshow(msk)
                axs1[1,0].set_title('binary & COM') 
                axs1[1,0].plot(ym,xm,'ro')  
                print("a20a:" + titl + str("frame") + str(fri))
        #end result:
        axs1[1,1].plot(all_xg,'ro',markersize=2)
        axs1[1,1].set_title('XY-tracked') 
        axs1[1,1].plot(all_yg,'bo',markersize=2)
        axs1[1,1].plot(all_R_minor,'ko',markersize=2)
        axs1[1,1].plot(all_rmaj,'mo',markersize=2)
        axs1[1,1].set_ylabel('position')
        axs1[1,1].set_xlabel('frame no.')
        axs1[1,1].legend(['X', 'Y', 'R_minor', 'R_major'],loc='best', fontsize='xx-small')
        outfig_name = out_path_name  + titl + str("frame") + str(fri)+ str("_track_example.png")
        fig1.savefig(outfig_name)
        plt.close()

        #save_mask:    
        maskname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(initval.tracking_key) + str("_BW.tif")
        io.imsave(maskpath / f"{maskname}", mask_stack, check_contrast=False)

        #set up csv for tracking data:
        csv_target=out_path_name  +str("file_")+ im_ori_name  + str("_roi")+str(roi_i) + "_xy_tracked.csv"
        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
            # create the csv writer
            writer = csv.writer(csv_f, delimiter=";")
            writer.writerow(
                    [
                        str("X"),
                        str("Y"),
                        str("R_minor"), 
                        str("R_major"),  
                    ]
                )
        #save tracking results per GUV as csv
        for fr_i, x in enumerate(all_xg):
            with open(csv_target, "a",newline='') as csv_f:  
                # create the csv writer
                writer = csv.writer(csv_f, delimiter=";")    
                writer.writerow(
                    [
                        all_xg[fr_i],
                        all_yg[fr_i],
                        all_R_minor[fr_i], 
                        all_rmaj[fr_i],
                    ]
                )
        

def a20b_map_color_channels(im_ori_name,guv_xyr,initval):
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
    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        #color_i=initval.tracking_key
        ##load csv::
        csv_source=in_path_name_tracked  +str("file_")+ im_ori_name  + str("_roi")+str(roi_i) + "_xy_tracked.csv"

        all_xg,all_yg,all_R_minor, all_R_major = guv_io.get_XY_info(csv_source)
        data_out=np.vstack((all_xg, 
                            all_yg, 
                            all_R_minor,
                            all_R_major))
        header_out=[str("X"), str("Y"),  str("R_minor"), str("R_major")]

        fig1, axs1=plt.subplots(2,3)
        for color_i in np.arange(3):     
            #load tracking channel:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            maskname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(initval.tracking_key) + str("_BW.tif")
            roi_stack=io.imread(roipath / f"{roiname}")
            mask_stack=io.imread(maskpath / f"{maskname}")
            roi_shp=np.shape(roi_stack)
            if len(roi_shp)==2:
                n_frames=1
            if len(roi_shp)==3: #stack
                n_frames=roi_shp[0]
            all_inside_I=[]
            all_edge_I=[]
            all_outside_I=[]
            for fri in np.arange(n_frames):
                if len(roi_shp)==2:
                    roi=roi_stack
                if len(roi_shp)==3: #stack
                    roi=roi_stack[fri,:,:]
                    mask=mask_stack[fri,:,:]
                xm=all_xg[fri]
                ym=all_yg[fri]
                rm=all_R_major[fri]
                if np.max(np.array(roi))>0:
                    #B. use the track coordinates to force-map the original image 
                    map = guv_tools.track_radial_pattern(roi*(~mask), runmodus=0, x0=xm,y0=ym, mapradius=rm, demo=0)[2]
                    if 0: 
                        #crop on twice the object radius: note that radials are in half-pixel units
                        radials =np.shape(map)[0]
                        if rm>1: 
                            cropit=int(np.min([2*2*rm, radials]))
                            map=map[0:cropit,:]
                   
                    #to do: analyze_map (inside_I, outside_I)
                    inside_radial_limit=int(0.5*2*rm)  #in half-pixel units
                    outside_radial_limit=int(1.1*2*rm)   #in half-pixel units
                    all_inside_I.append(np.mean(map[0:inside_radial_limit]))
                    all_edge_I.append(np.median(np.max(map, axis=0)))
                    all_outside_I.append(np.mean(map[outside_radial_limit:-1]))
                    dum=1
                else:
                    all_inside_I.append(0)
                    all_edge_I.append(0)
                    all_outside_I.append(0)
                    #process the work image
                titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
                if  fri==0:
                    #show track example: 
                    axs1[0,color_i].imshow(map)
                    axs1[0,color_i].set_title(str("color") + str(color_i)) 
                    print("a20b:" + titl + str("frame") + str(fri))
            #end result:
            axs1[1,color_i].plot(all_inside_I,'ro', markersize=2)
            axs1[1,color_i].plot(all_edge_I,'bo',markersize=2)
            axs1[1,color_i].plot(all_outside_I,'ko',markersize=2)
            axs1[1,color_i].legend(['inside', 'edge', 'outside'],loc='best', fontsize='xx-small')
            color_data=np.vstack((all_inside_I, 
                                  all_edge_I, 
                                  all_outside_I))
            color_header=[str("color") + str(color_i)+str("_inside"), 
                          str("c") + str(color_i)+str("_edge"),
                          str("c") + str(color_i)+str("_outside"),
                        ]
            data_out=np.vstack((data_out,color_data))
            header_out=np.hstack((header_out, color_header))
        dum=1
        #final savings:
        outfig_name = out_path_name  + titl + str("frame") + str(fri)+ str("_intensities.png")
        fig1.savefig(outfig_name)
        plt.close()

        #scv:
        csv_target=out_path_name  +str("file_")+ im_ori_name  + str("_roi")+str(roi_i) + "_all_data.csv"
        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
            # create the csv writer
            writer = csv.writer(csv_f, delimiter=";")
            writer.writerow(header_out)
        #save results per GUV as csv
        for row in np.transpose(data_out):
            with open(csv_target, "a",newline='') as csv_f:  
                # create the csv writer
                writer = csv.writer(csv_f, delimiter=";")    
                writer.writerow(row)
        dum=1


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
