""" vesicle data input-output
Jacob Kers 2024

 """
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
#from readlif.reader import LifFile
from pathlib import Path
import csv
from skimage import io
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import guv_tools
from PIL import Image, ImageSequence
import nd2

class Event:
    def __init__(self, row_dict):
        self.data = row_dict  # Store the row data as a dictionary

    def __repr__(self):
        return f"Event({self.data})"


def read_csv_to_events(file_path):
    events = []
    
    # Open the CSV file and read its contents
    with open(file_path, mode='r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)  # Automatically uses headers as keys
        
        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Create an Event object for each row
            event = Event(row)
            events.append(event)
    
    return events

def load_tiff_frame(file_path, frame_index):
    # Open the TIFF file
    with tf.TiffFile(file_path) as tif:
        # Load a specific frame (zero-indexed)
        frame = tif.pages[frame_index].asarray()
    return frame

def load_tiff_movie_as_array(input_path):
    """Load a TIFF movie as a 3D NumPy array (frames, height, width)."""
    with Image.open(input_path) as img:
        frames = []
        while True:
            frames.append(np.array(img))  # Convert each frame to a NumPy array
            try:
                img.seek(img.tell() + 1)
            except EOFError:
                break
    
    return np.stack(frames)  # Convert list of frames into a 3D NumPy array

def load_tiff_movie(input_path):
    """Load a TIFF movie as a list of frames."""
    with Image.open(input_path) as img:
        frames = []
        while True:
            frames.append(img.copy())
            try:
                img.seek(img.tell() + 1)
            except EOFError:
                break
    return frames

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


def get_XY_info(csv_source):
    """ ead roi data as acquired via ImageJ:
    ImageJ area selection
    * Open BF or Phase image
    * Select "round" ROI (keep Shift pressed for a circle)
    * Find the position and press "T" to load it into the ROI manager (check "show all" box)
    * Click into the ROI manager window and CTRL+A to select all ROIs
    * CLick More>list>File>Save As> ".....csv"
    * for convenience, you might just save the screenshots with overlays """
    X = []
    Y = []
    R_minor = []
    R_major = []
    areas=[]
    perimeters=[]
    roundness=[]
    with open(csv_source) as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            X.append(float(row["X"]))
            Y.append(float(row["Y"]))
            R_minor.append(float(row["R_minor"]))
            R_major.append(float(row["R_major"]))
            areas.append(float(row["area"]))
            perimeters.append(float(row["perimeter"])) 
            roundness.append(float(row["roundness"]))
    return X, Y,R_minor, R_major, areas, perimeters, roundness

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

    return XX0,YY0,RR0

def get_drift_info_tracked(roi_id,initval):
    csv_path= initval.mainpath_out + initval.subdir +str("/A20a_tracked/")
    csv_name=str("file_")+ roi_id + str("_xy_tracked.csv")
    csv_source= csv_path + csv_name
    Xt = []
    Yt = []
    width = []
    with open(csv_source) as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            Xt.append(float(row["X"]))
            Yt.append(float(row["Y"]))
    #zero on first point, zero-tracks unchanged
    X0=Xt[0]
    Y0=Yt[0]
    for ii,X in enumerate(Xt):
        if X>0:
            Xt[ii]=Xt[ii]-X0
            Yt[ii]=Yt[ii]-Y0

    return Xt,Yt

def get_drift_info(csv_source,initval):
    """ 
    prepare an extimate of the drift usijg pre-clicked coordinates 
    """
    Td = []
    Xd = []
    Yd = []
    width = []
    with open(csv_source) as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            Td.append(float(row["Frame"])-1)
            Xd.append(float(row["X"]))
            Yd.append(float(row["Y"]))
    
    
    #make sure drift vector is long enough: add some extra frame steps 
    last_driftX=Xd[-1]-Xd[-2]
    last_driftY=Xd[-1]-Xd[-2]
    last_T=Td[-1]
    extra_t=float(0)
    for extra_t in np.arange(5.0):
        Td.append(extra_t + last_T)
        Xd.append(Xd[-1]+last_driftX)
        Yd.append(Yd[-1]+last_driftY)
    Xd=(np.array(Xd)-Xd[0])/initval.pix2mu
    Yd=(np.array(Yd)-Yd[0])/initval.pix2mu
    Td=np.array(Td)
    
    Ti = np.arange(np.max(Td))
    Xi = np.interp(Ti, Td, Xd)
    Yi = np.interp(Ti, Td, Yd)
 
    if 0:
        fig, axs = plt.subplots(1,1)
        axs.plot(Td,Xd, 'ro')
        axs.plot(Td,Yd, 'bo')
        axs.plot(Ti,Xi, 'r-')
        axs.plot(Ti,Yi, 'b-')
        fig.show()
        dum=1

    return Xi,Yi


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

def cut_tif_to_roi_tiffs_hardwired(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .tif  format
    Since Fiji exports seem to differ in how python interprets the format (unwanted merging of color channels), here we re-shape the tiffstack if needed
    #Jacob 2024 """ 
    # load the stack by simple tiff reading
    # check the shape
    # check the intended number of colors
    # re-shape accordingly and run loops to split colors
    
    #standard setting up:
    source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
    datapath_out_name = initval.mainpath_out + initval.subdir 
    roipath_name = initval.mainpath_out + initval.subdir +str("/A10_rois")
    overviewpath_name = initval.mainpath_out + initval.subdir +str("/A100_overviews")
    
    outpath = Path(datapath_out_name)
    overviewpath= Path(overviewpath_name)
    if not outpath.is_dir():
        outpath.mkdir()
       
    roipath = Path(roipath_name)
    if not roipath.is_dir():
        roipath.mkdir() 
        overviewpath.mkdir()  
    #simple load:
    st = io.imread(source)
    idx=np.argmin(np.shape(st))
    st=np.moveaxis(st,idx,0)  #CTXY for easy color split
    nc,ff,dx,dy=np.shape(st)

    

    #work each GUV and its center coordinates:
    fig, axs = plt.subplots(1,1)
    for roi_i, cd in enumerate(guv_xyr):  
        roi_id=im_ori_name + str("_roi")+str(roi_i) 
        if initval.apply_drift_correction==2:
                    X_tr,Y_tr=get_drift_info_tracked(roi_id, initval)                   
        for color_i, color_i_trace in enumerate(st):
            for fri, chan in enumerate(color_i_trace):                  
                #cut (we assume roi just fits the vesicle)
                extra_space=2       
                x0 = cd[0]
                y0 = cd[1]
                if initval.apply_drift_correction==1:
                    x0=int(x0+initval.driftX[fri])
                    y0=int(y0+initval.driftY[fri])
                if initval.apply_drift_correction==2:
                    x0=int(x0+X_tr[fri])
                    y0=int(y0+Y_tr[fri])
                r0 = int(cd[2]*extra_space)
                #get image or stack:             
                roi_1frame = guv_tools.get_roi(chan, x0, y0, r0)
                if fri==0:
                    rr,cc=np.shape(roi_1frame)
                    roi=np.zeros((ff,rr,cc),dtype=int)
                roi[fri,:,:]=roi_1frame
                
                # save overview plots per GUVp, last channel
                if roi_i==0 and fri==0:
                    ovv_im=np.log(chan)
                if fri == 0:
                    ovv_im=guv_tools.highlight_roi(ovv_im, x0, y0, r0)
                    axs.imshow(ovv_im)
                    axs.set_title(im_ori_name)
                    fontprops = fm.FontProperties(size = 8, family = 'serif')
                    kwargs_ = {
                            'fontproperties': fontprops,
                            'color': 'white',
                            }
                    kwargs_.update(kwargs_)
                    axs.annotate(str(roi_i), xy = (x0-6, y0+6), xycoords = 'data',  **kwargs_)
                    fig.tight_layout()             

            #build a savename, save the tiff:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            print(str("a10:") + roiname)
            io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
            
               
    fig.show()
    overviewname=str("from_")+ im_ori_name + str("_roi_overview.png")
    fig.savefig(overviewpath / f"{overviewname}")
    dum=1



    dum=1
    """ st = tiff_in #loads as TXY
    st = np.reshape(st, st.shape + (1, ))
   
    shrink_tiff=st
 """


def cut_tif_to_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .tif  format
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
    N_guvs, dum = np.shape(guv_xyr)
    
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
        fig, axs = plt.subplots(1,initval.N_colors)
        for color_i in np.arange(initval.N_colors):
            for fri, frame in enumerate(ImageSequence.Iterator(RGB_tif)):  
                chan_pil=frame.split()[color_i]
                chan = np.array(chan_pil)      
                #cut (we assume roi just fits the vesicle)
                extra_space=2
                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*extra_space
                #get image or stack:  
                chan = np.array(chan_pil)            
                roi_1frame = guv_tools.get_roi(chan, x0, y0, r0)
                if fri==0:
                    rr,cc=np.shape(roi_1frame)
                    ff=int(info_dict["Frames in Image"])
                    roi=np.zeros((ff,rr,cc),dtype=int)
                roi[fri,:,:]=roi_1frame
                
                # save overview plots per GUVp
                if fri == 0:
                    axs[color_i].imshow(roi[0,:,:])
                    axs[color_i].set_title(color_i)
                    fig.tight_layout()
            #build a savename, save the tiff:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            print(str("a10:") + roiname)
            io.imsave(roipath / f"{roiname}", roi, check_contrast=False)
            dum=1

def cut_singletime_tif_to_roi_tiffs(im_ori_name,guv_xyr,initval):
    """ use pre-set coordinates in imageJ to save standardized tif roi-stacks from .tif  format
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
    N_guvs, dum = np.shape(guv_xyr)
    
    #loop: 'images' contains all colors and all frames
    #RGB_tif = Image.open(source)
    RGB_tif = io.imread(source)
    # extract other basic metadata
    rr,cc,ff,=np.shape(RGB_tif)
    for roi_i, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
        fig, axs = plt.subplots(1,initval.N_colors)
        #for single-time tiffs, the sequence just lists the for colors
        #thus, the nth frame should be chosen for this color.
        for color_i in np.arange(ff):  
            frame= RGB_tif[:,:,color_i]    
            #cut (we assume roi just fits the vesicle)
            extra_space=2
            x0 = cd[0]
            y0 = cd[1]
            r0 = cd[2]*extra_space
            #get image or stack:  
            #chan = np.array(frame)            
            roi_1frame = guv_tools.get_roi(frame, x0, y0, r0)
            rr,cc=np.shape(roi_1frame)
            if color_i==0:  
                roi_all_colors=np.zeros((ff,rr,cc),dtype=int)
            # overview plots per GUVp:
            axs[color_i].imshow(roi_all_colors[color_i,:,:])
            axs[color_i].set_title(color_i)
            fig.tight_layout()
            roi_all_colors[color_i,:,:]=roi_1frame
            #build a savename, save the tiff:
            roiname=str("from_")+ im_ori_name + str("_roi")+str(roi_i) + str("_c")+str(color_i) + str(".tif")
            print(str("a10:") + roiname)
            io.imsave(roipath / f"{roiname}", roi_1frame, check_contrast=False)
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
            else:
                roi0=roi_stack #single image
            roi0=roi0-np.min(roi0)
            #roi0=guv_tools.donut_mask_it(roi0)
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
          