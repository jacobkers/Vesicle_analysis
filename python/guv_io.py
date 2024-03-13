""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from readlif.reader import LifFile
from pathlib import Path
import csv
from skimage import io
import matplotlib.pyplot as plt
import guv_tools
from PIL import Image, ImageSequence


def get_roi_info(csv_source):
    """ ead roi data as acquired via ImageJ:
    ImageJ area selection
    * Open BF or Phase image
    * Select "round" ROI (keep Shift pressed for a circle)
    * Find the position and press "T" to load it into the ROI manager (check "show all" box)
    * Click into the ROI manager window and CTRL+A to select all ROIs
    * CLick More>list>File>Save As> ".....csv"
    * for convenience, you might just save the screenshots with overlays """
    Xc = []
    Yc = []
    width = []
    with open(csv_source) as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            Xc.append(float(row["X"]))
            Yc.append(float(row["Y"]))
            width.append(float(row["Width"]))

    XX0 = np.array(Xc) + np.array(width) / 2
    YY0 = np.array(Yc) + np.array(width) / 2
    RR0 = np.array(width) / 2

    return XX0, YY0, RR0


def cut_nd2_to_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from Nikon .nd2 format
    #Jacob 2024 """
    source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A10_overview/")
    outpath = Path(datapath_out_name)
    roipath = Path(roipath_name)
    overviewpath = Path(overviewpath_name)
    if not outpath.is_dir():
        outpath.mkdir()
    if not roipath.is_dir():
        roipath.mkdir()
    if not overviewpath.is_dir():
        overviewpath.mkdir()
    N_guvs, dum = np.shape(guv_xyr)
    fig, axs = plt.subplots(N_guvs + 1, 4)
    #nd_format reader:
    #loop: 'images' contains all colors and all frames
    with nd2reader.Nd2(source) as images:
        for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
            for (
                color_i,
                chan,
            ) in enumerate(images):  #work each color channel per guv              
                #map, show, save:
                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*.15
                #get image or stack:              
                roi = guv_tools.get_roi(chan, x0, y0, r0)                         
                #build work image via the various channels-------------------------------------------   
                if color_i==0: #setup a work image for edge detection etc
                  #work_image=guv_tools.sobel_it(roi)
                  work_image=roi
                #else:
                  #work_image=work_image+guv_tools.sobel_it(roi)                               
                # plotting cosmetics:-------------------------------------------
                axs[roi_i + 1, color_i].imshow(roi)               
                axs[0, color_i].imshow(chan)
                axs[0, color_i].set_title(images.channels[color_i])
                #build a savename:
                roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
                io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
        #saving of overviews:                
        fig.tight_layout()
        fig.show()
        outfig_name1 = overviewpath_name  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig_name1)             
        


def cut_lif_to_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .lif  format
    #Jacob 2024 """
    source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A10_overview/")
    outpath = Path(datapath_out_name)
    roipath = Path(roipath_name)
    overviewpath = Path(overviewpath_name)
    if not outpath.is_dir():
        outpath.mkdir()
    if not roipath.is_dir():
        roipath.mkdir()
    if not overviewpath.is_dir():
        overviewpath.mkdir()
    N_guvs, dum = np.shape(guv_xyr)
    fig, axs = plt.subplots(N_guvs + 1, 4)
    #nlif _format reader:
    #loop: 'images' contains all colors and all frames

    get_lifs= LifFile(source)
    lif_list = [i for i in get_lifs.get_iter_image()]

    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
    #walk the frames:
        for lif_objects in lif_list:
            # Access a specific item
            # Iterate over different items
            frame_list   = [i for i in lif_objects.get_iter_t(c=0, z=0)]
            z_list       = [i for i in lif_objects.get_iter_z(t=0, c=0)]
            channel_list = [i for i in lif_objects.get_iter_c(t=0, z=0)]
            for color_i in np.arange(len(channel_list)):
                for fr_i in np.arange(len(frame_list)):
                    chan_pil=lif_objects.get_frame(z=0, t=fr_i, c=color_i)
                    #map, show, save:
                    x0 = cd[0]
                    y0 = cd[1]
                    r0 = cd[2]*1.5
                    #get image or stack:  
                    chan = np.array(chan_pil)            
                    roi = guv_tools.get_roi(chan, x0, y0, r0)
                    # plotting cosmetics:-------------------------------------------
                    axs[roi_i + 1, color_i].imshow(roi)               
                    axs[0, color_i].imshow(chan)
                    axs[0, color_i].set_title(color_i)
                    #build a savename:
                    roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
                    io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
                    #saving of overviews:                
        fig.tight_layout()
        fig.show()
        outfig_name1 = overviewpath_name  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig_name1)             
        dum=1


def cut_tif_to_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .lif  format
    #Jacob 2024 """
    source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    
    outpath = Path(datapath_out_name)
    if not outpath.is_dir():
        outpath.mkdir()
    roipath = Path(roipath_name)
    if not roipath.is_dir():
        roipath.mkdir()
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A10_overview/")
    overviewpath = Path(overviewpath_name)
    if not overviewpath.is_dir():
        overviewpath.mkdir()
    N_guvs, dum = np.shape(guv_xyr)
    fig, axs = plt.subplots(N_guvs + 1, 4)
    #nlif _format reader:
    #loop: 'images' contains all colors and all frames
    RGB_tif = Image.open(source)
    # extract other basic metadata
    info_dict = {
        "Filename": RGB_tif.filename.split('/')[1],
        "Image Size": RGB_tif.size,
        "Image Height": RGB_tif.height,
        "Image Width": RGB_tif.width,
        "Image Format": RGB_tif.format,
        "Image Mode": RGB_tif.mode,
        "Image is Animated": getattr(RGB_tif, "is_animated", False),
        "Frames in Image": getattr(RGB_tif, "n_frames", 1),
    }

    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        for color_i in np.arange(3):
            for fri, frame in enumerate(ImageSequence.Iterator(RGB_tif)):  
                chan_pil=frame.split()[color_i]
                chan = np.array(chan_pil)      
                #cut
                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*1.5
                #get image or stack:  
                chan = np.array(chan_pil)            
                roi_1frame = guv_tools.get_roi(chan, x0, y0, r0)
                if fri==0:
                    rr,cc=np.shape(roi_1frame)
                    ff=int(info_dict["Frames in Image"])
                    roi=np.zeros((ff,rr,cc),dtype=int)
                roi[fri,:,:]=roi_1frame
            # plotting cosmetics:-------------------------------------------
            axs[roi_i + 1, color_i].imshow(roi[0,:,:])               
            axs[0, color_i].imshow(chan)
            axs[0, color_i].set_title(color_i)
            #build a savename:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
            #saving of overviews:                
        fig.tight_layout()
        fig.show()
        outfig_name1 = overviewpath_name  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig_name1)             
        dum=1

def work_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .lif  format
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
            fig2, ax2 = guv_tools.work_radial_pattern(roi0)
            fig2.show() 
            outfig_name2 = overviewpath_name  + str("file_")+ im_ori_name  + str("_roi")+str(roi_i) +  str("c") + str(color_i) + str("frame") + str(0) + str("_QI_track.png")
            fig2.savefig(outfig_name2)
            plt.close()
            # plotting cosmetics
            axs[color_i].imshow(roi0)               
            axs[color_i].imshow(roi0)
            axs[color_i].set_title(color_i)
        fig.tight_layout()
        fig.show()
        plt.close("all")

        dum=1
          
""" 
               
                
                #get image or stack:              
                roi = guv_tools.get_roi(chan, x0, y0, r0)                         
                #build work image via the various channels-------------------------------------------   
                if color_i==0: #setup a work image for edge detection etc
                    #work_image=guv_tools.sobel_it(roi)
                    work_image=roi
                #else:
                    #work_image=work_image+guv_tools.sobel_it(roi)                                
                # plotting cosmetics:-------------------------------------------
                axs[roi_i + 1, color_i].imshow(roi)               
                axs[0, color_i].imshow(chan)
                axs[0, color_i].set_title(images.channels[color_i])
                #build a savename:
                roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
                io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
        #saving of overviews:                
        fig.tight_layout()
        fig.show()
        outfig_name1 = overviewpath_name  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig_name1)             
        #process the work image
        fig2, ax2 = guv_tools.work_radial_pattern(work_image, x0,y0,r0)
        fig2.show() 
        outfig_name2 = overviewpath_name  + str("file_")+ im_ori_name  + str("frame") + str(1) + str("_QI_track.png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig2.savefig(outfig_name2)
        plt.close("all") """