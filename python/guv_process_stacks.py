""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import io
import guv_tools
import cv2
def build_coordinates(im_ori_name,guv_xyr,initval):
    """ collect relevant coordinates (such as guv center) from tiff stacks and save as csv
#Jacob 2024 """
 
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
        
        if len(roi_shp)==2:
            n_frames=1
        if len(roi_shp)==3: #stack
            n_frames=roi_shp[0]
        all_xq=[]
        all_yq=[]
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
                roi_tr= roi.astype(int)
                roi_tr= guv_tools.treshold_it(roi)[0]
                roi_tr=guv_tools.sobel_it(roi) 
                #track!:
                xq,yq = guv_tools.track_radial_pattern(roi_tr, runmodus=1, demo=0)[0:2]
                all_xq.append(xq)
                all_yq.append(yq)
                #map on original roi using these coordinates:
                #B. use the track coordinates to force-map the original image 
                map = guv_tools.track_radial_pattern(roi, runmodus=0, x0=xq,y0=yq,demo=0)[2]
                #to do: analyze_map (inside_I, outside_I)
                all_inside_I.append(np.median(map[1]))
                all_edge_I.append(np.median(np.max(map, axis=0)))
                all_outside_I.append(np.median(map[-1]))
                dum=1
            else:
                all_xq.append(0)
                all_yq.append(0)
                all_inside_I=(0)
                all_edge_I=(0)
                all_outside_I=(0)
                #process the work image
            if fri==0:
                #demo_save, forced mapping on last 'work' image:
                fig1, axs1 = guv_tools.track_radial_pattern(roi_tr, runmodus=0, x0=xq,y0=yq,demo=1)  
                #show track example:
                titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i)
                outfig_name1 = overviewpath_name  + titl + str("frame") + str(0)+ str("_QI_mapped.png")
                fig1.savefig(outfig_name1)
                plt.close()
            if fri == n_frames-1:
                #show trace example
                fig2, axs2=plt.subplots(2,2)
                axs2[0,0].plot(all_xq,'ro',linewidth=0.3)
                axs2[0,0].set_title('tracked by QI') 
                axs2[0,0].plot(all_yq,'bo',linewidth=0.3)
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
                axs2[1,1].set_title('edge_I') 
                axs2[1,1].set_ylabel('intensity, a.u.')
                axs2[1,1].set_xlabel('frame no.')
                outfig_name2 = overviewpath_name  + titl + str("frame") + str(0)+ str("_QI_tracked.png")
                fig2.savefig(outfig_name2)
                plt.close()


def work_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to processed standardized tif roi-stacks from  format
    #Jacob 2024 """
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A20_processed/")
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
            #roi0=guv_tools.donut_mask_it(roi0)
            #in this section, build the 'workimage'
            
            #show the color channel
            fig, axs = plt.subplots(1,1)
            axs.imshow(roi0)
            titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i) + str("frame") + str(0)
            axs.set_title(titl) 
            outfig_name = overviewpath_name  + titl + str(".png")
            fig.savefig(outfig_name)
            plt.close()
