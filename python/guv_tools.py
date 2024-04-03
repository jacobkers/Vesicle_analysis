""" #guv_tools
#tools to work with guv files: """
import numpy as np
import matplotlib.pyplot as plt
#import nd2reader
#from readlif.reader import LifFile
from pathlib import Path
import cv2
import csv
from skimage import io
from scipy.ndimage import sobel
from qi_trak import QI_Tracker
import matplotlib.pyplot as plt

def work_radial_pattern(roi):
    roi_array = np.array(roi)  #for tracking                
    # QI_track on one channel
    rr=np.shape(roi)[0]
    r0=rr/2
    QI=QI_Tracker(roi_array)
    preset=QI_Tracker.TrackXY_by_QI_Init(QI,roi_array)                                                           
    xq, yq, allprofiles = QI_Tracker.TrackXY_by_QI(QI,roi_array, preset, r0, r0)    
    fig, axs = plt.subplots(1,2)
    plotgridx=preset["X0samplinggrid"]+xq
    plotgridy=preset["Y0samplinggrid"]+yq
    axs[0].imshow(roi)
    lx=np.shape(plotgridx)
    axs[0].plot(plotgridx[::10,::20],plotgridy[::10,::20],'r-',linewidth=0.3)
    axs[0].plot(xq,yq,'rx')
    axs[0].set_title('tracked by QI') 
    axs[1].imshow(allprofiles)
    axs[1].set_title('polar map') 
    fig.tight_layout()
    
    return fig,axs

def get_roi(image,x0,y0,r0):
    """
    basic collection of points
    'image' can also be a stack
    @author: jkerssemakers, 2024
    """
    #cuts square area with inscribed radius r0. If outside-roi, roi is shifted
    dims =np.shape(image)
    
    lox=int(max([0, x0 - r0]))
    hix=int(min([dims[0], x0+r0]))
    loy=int(max([0, y0 - r0]))
    hiy=int(min([dims[1], y0+r0]))
    if len(dims)==2:
        roi = image[loy:hiy, lox:hix]
    if len(dims)==3:
        roi = image[loy:hiy, lox:hix,:]

    return roi

def sobel_it(roi):
    roi = roi.astype(float)
    roi = cv2.filter2D(roi, -1, 5)
    sobel_h = sobel(roi, 0)  # horizontal gradient
    sobel_v = sobel(roi, 1)  # vertical gradient
    magnitude = np.sqrt(sobel_h**2 + sobel_v**2)
    magnitude=np.array(magnitude.astype(int))
    #magnitude *= 255.0 / np.max(magnitude)  # normalization
    return magnitude

def donut_mask_it(roi):
    """
    make donut-shaped mask to improve QI tracking of versicle edge.
    Note: we assume a roi is taken as 3 times the approximate vesicle diameter (thus, we expet the vesicle edge at about 2/3* half the image size)
    @author: jkerssemakers, 2024
    """
    rr,cc =np.shape(roi)
    #rr, cc=50, 50
    approx_rim=rr/2*(2/3)  #see above
    rim_lo=0.5*approx_rim
    rim_hi=1.5*approx_rim
    rim_sharpness=rr/40
    x, y = np.linspace(-cc / 2, cc / 2, cc), np.linspace(-rr / 2, rr / 2, rr)
    X, Y = np.meshgrid(x, y)
    radii = np.hypot(X, Y)
    donut_mask=0*radii+1
    #smooth band:
    if 0:
        donut_mask[radii<rim_lo]=0
        donut_mask[radii>rim_hi]=0
        rimsmooth_lo=1-np.exp(-(radii-rim_lo)/rim_sharpness)
        rimsmooth_hi=1-np.exp(-(rim_hi-radii)/rim_sharpness)
        donut_mask=donut_mask*rimsmooth_lo*rimsmooth_hi
        roi_out=roi*donut_mask
    else:
        roi_out=roi
        roi_out[radii<rim_lo]=np.median(roi[radii<rim_lo])
        roi_out[radii>rim_hi]=np.median(roi[radii>rim_hi])
    if 0: #test
        fig, axs = plt.subplots(1,1)
        axs.imshow(255*donut_mask)
        #axs.plot(donut_mask)
        fig.tight_layout()
        fig.show()

    return roi_out
