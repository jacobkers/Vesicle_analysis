""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skimage import io
import guv_tools
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
        if len(roi_shp)==3: #work stack
            roi0=roi_stack[0,:,:] 
            #walk frames [empty]:
            for roi in roi_stack:
                dum=1
                #process the work image
        else:
            roi0=roi_stack #single image
        #in this section, build the 'workimage'
        roi0=roi0-np.min(roi0)
        roi0_sobel=guv_tools.sobel_it(roi0)
        fig, axs = guv_tools.work_radial_pattern(roi0_sobel)   
        #show the result
        titl = str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i) + str("frame") + str(0) + str("_sobel_QI_track")
        outfig_name = overviewpath_name  + titl + str(".png")
        fig.savefig(outfig_name)
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
