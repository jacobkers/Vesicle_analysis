""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import io
import guv_tools
import guv_binary_ops
import cv2
import csv

def build_coordinates(im_ori_name,guv_xyr,initval):
    """ collect relevant coordinates (such as guv center) from tiff stacks and save as csv
#Jacob 2024 """
    #set apaths:
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A20_processed/")
    roipath = Path(roipath_name)
    overviewpath = Path(overviewpath_name)
    if not overviewpath.is_dir():
        overviewpath.mkdir()
   
    fig, axs = plt.subplots(1, 3)

    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        color_i=initval.tracking_key
        #load tracking channel:
        roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
        roi_stack=io.imread(roipath / f"{roiname}")
        roi_shp=np.shape(roi_stack)
        #set up csv for tracking data:
        csv_target=overviewpath_name  +str("file_")+ im_ori_name  + str("_roi")+str(roi_i) + "_xy_tracked.csv"
        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
            # create the csv writer
            writer = csv.writer(csv_f, delimiter=";")
            writer.writerow(
                    [
                        str("X"),
                        str("Y"),
                        str("R"),  
                    ]
                )


        if len(roi_shp)==2:
            n_frames=1
        if len(roi_shp)==3: #stack
            n_frames=roi_shp[0]
        all_xg=[]
        all_yg=[]
        all_rg=[]
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
                roi_tr=guv_tools.smooth_it(roi_tr,labda=3)
                roi_tr= roi_tr.astype(int)
                roi_tr= guv_tools.treshold_it(roi_tr)[0]
                roi_tr=guv_tools.sobel_it(roi_tr)   
                #roi_tr=guv_tools.smooth_it(roi_tr,labda=1)
                #transfer to binary operations to gat masks and robust coordinates
                msk, BW_edge, xm, ym, rm = guv_binary_ops.work_binaries(roi_tr)                    
                all_xg.append(xm)
                all_yg.append(ym)
                all_rg.append(rm)           
            else:
                all_xg.append(0)
                all_yg.append(0)
                all_rg.append(0) 

            #build and save summary figure:    
            titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
            if  fri==0:
                #show track example:
                fig1, axs1=plt.subplots(2,2)
                axs1[0,0].imshow(roi)
                axs1[0,0].set_title('original') 
                axs1[0,1].imshow(roi_tr)
                axs1[0,1].set_title('work_image')
                axs1[0,1].plot(all_yg,all_xg,'ro')
                axs1[1,0].imshow(msk)
                axs1[1,0].set_title('binary & COM') 
                axs1[1,0].plot(ym,xm,'ro')  
                print(titl + str("frame") + str(fri))
        #end result:
        axs1[1,1].plot(all_xg,'ro',linewidth=0.3)
        axs1[1,1].set_title('XY-tracked') 
        axs1[1,1].plot(all_yg,'bo',linewidth=0.3)
        axs1[1,1].plot(all_rg,'k',linewidth=0.3)
        axs1[1,1].set_ylabel('position')
        axs1[1,1].set_xlabel('frame no.')
        axs1[1,1].legend(['X', 'Y', 'R_minor'])
        outfig_name = overviewpath_name  + titl + str("frame") + str(fri)+ str("_track_example.png")
        fig1.savefig(outfig_name)
        plt.close()
        #save tracking results per GUV as csv
        for fr_i, x in enumerate(all_xg):
            with open(csv_target, "a",newline='') as csv_f:  
                # create the csv writer
                writer = csv.writer(csv_f, delimiter=";")    
                writer.writerow(
                    [
                        all_xg[fr_i],
                        all_yg[fr_i],
                        all_rg[fr_i],   
                    ]
                )
        

def map_color_channels(im_ori_name,guv_xyr,initval):
    """ collect values from various color channels
#Jacob 2024 """
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A20b_processed/")
    roipath = Path(roipath_name)
    overviewpath = Path(overviewpath_name)
    if not overviewpath.is_dir():
        overviewpath.mkdir()
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
        all_inside_I=[]
        all_edge_I=[]
        all_outside_I=[]
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
                roi_tr=guv_tools.smooth_it(roi_tr,labda=4)
                roi_tr= roi_tr.astype(int)
                roi_tr= guv_tools.treshold_it(roi_tr)[0]
                roi_tr=guv_tools.sobel_it(roi_tr)   
                roi_tr=guv_tools.smooth_it(roi_tr,labda=1)
                #transfer to binary operations to gat masks and robust coordinates
                msk, BW_edge, xm, ym, rm = guv_binary_ops.work_binaries(roi_tr)     
                # QI-track the work image to get coordinates (from com first guess):
                xq,yq = guv_tools.track_radial_pattern(roi_tr*msk, runmodus=1, demo=0)[0:2]
                #Radial-map on original roi using these coordinates:
                #B. use the track coordinates to force-map the original image 
                map = guv_tools.track_radial_pattern(roi, runmodus=0, x0=xm,y0=ym,demo=0)[2]
                #crop on twice the object radius: note that radials are in half-pixel units
                radials =np.shape(map)[0]
                cropit=int(np.min([2*2*rm, radials]))
                map=map[0:cropit,:]
                
                all_xg.append(xm)
                all_yg.append(ym)
                #to do: analyze_map (inside_I, outside_I)
                inside_radial_limit=int(0.5*2*rm)  #in half-pixel units
                outside_radial_limit=int(1.1*2*rm)   #in half-pixel units
                all_inside_I.append(np.mean(map[0:inside_radial_limit]))
                all_edge_I.append(np.median(np.max(map, axis=0)))
                all_outside_I.append(np.mean(map[outside_radial_limit:-1]))
                dum=1
            else:
                all_xg.append(0)
                all_yg.append(0)
                all_inside_I.append(0)
                all_edge_I.append(0)
                all_outside_I.append(0)
                #process the work image
            titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
            if  fri==0:
                #demo_save, forced mapping on last 'work' image:
                map = guv_tools.track_radial_pattern(roi*msk, runmodus=0, x0=xm,y0=ym,demo=0)[2]
                map=map[0:cropit,:]
                #show track example:
                fig1, axs1=plt.subplots(2,2)
                axs1[0,0].imshow(roi)
                axs1[0,0].set_title('original') 
                axs1[0,1].imshow(roi_tr)
                axs1[0,1].set_title('track_image')
                axs1[0,1].plot(yq,xq,'ro') 
                axs1[1,0].imshow(msk)
                axs1[1,0].set_title('mask/Centroid') 
                axs1[1,0].plot(ym,xm,'ro') 
                axs1[1,1].imshow(map)
                axs1[1,1].set_title('mapped') 
                outfig_name1 = overviewpath_name  + titl + str("frame") + str(fri)+ str("_QI_mapped.png")
                #fig1.show()
                print(titl + str("frame") + str(fri))
                fig1.savefig(outfig_name1)
                #plt.close()
            #summary figure for movie:
            if fri == n_frames-1:
                fig2, axs2=plt.subplots(2,2)
                axs2[0,0].plot(all_xg,'ro',linewidth=0.3)
                axs2[0,0].set_title('tracked') 
                axs2[0,0].plot(all_yg,'bo',linewidth=0.3)
                axs2[0,0].set_ylabel('position')
                axs2[0,0].set_xlabel('frame no.')
                axs2[0,1].plot(all_inside_I,'bo',linewidth=0.3)
                axs2[0,1].set_title('inside_I') 
                axs2[0,1].set_ylabel('intensity, a.u.')
                axs2[0,1].set_xlabel('frame no.')
                axs2[1,0].plot(all_edge_I,'ko',linewidth=0.3)
                axs2[1,0].set_title('edge_I') 
                axs2[1,0].set_ylabel('intensity, a.u.')
                axs2[1,1].set_xlabel('frame no.')
                axs2[1,1].plot(all_outside_I,'ko',linewidth=0.3)
                axs2[1,1].set_title('outside_I') 
                axs2[1,1].set_ylabel('intensity, a.u.')
                axs2[1,1].set_xlabel('frame no.')
                outfig_name2 = overviewpath_name  + titl + str("frame") + str(0)+ str("_QI_tracked.png")
                fig2.savefig(outfig_name2)
                plt.close()


def show_roi_overviews(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to processed standardized tif roi-stacks from  format
    #Jacob 2024 """
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A20a_overviews/")
    roipath = Path(roipath_name)
    overviewpath = Path(overviewpath_name)
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
            outfig_name = overviewpath_name  + titl + str(".png")
            fig.savefig(outfig_name)
            plt.close()
