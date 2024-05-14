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

def treshold_it(im):
    """ treshold by triangulation, following Margreet Docter 
    JacobKerts, 2023"""
    rr,cc=im.shape
    # sort and scale on number of pixels (to equalize axes)
    impixels=im.flatten()
    impixels_sorted=np.sort(impixels)
    Npix=len(impixels)
    pix_ax=np.arange(0, Npix, 1)
    Ipix=np.max(impixels)
    impixels_sorted=impixels_sorted/Ipix*Npix

    #fit on lower half of N:
    lowerhalf_N=impixels_sorted[0:int(Npix/2)]
    lowerhalf_pix_ax=pix_ax[0:int(Npix/2)]
    lowerfit_p=np.polyfit(lowerhalf_pix_ax,lowerhalf_N,1)
    lowerfit=np.polyval(lowerfit_p, pix_ax)

    #fit on higher half of I:
    upperhalf_I=impixels_sorted[impixels_sorted>Npix/2]
    upperhalf_pix_ax=pix_ax[impixels_sorted>Npix/2]
    upperfit_p=np.polyfit(upperhalf_pix_ax,upperhalf_I,1)
    upperfit=np.polyval(upperfit_p, pix_ax)
    #get cross-point
    xc=(lowerfit_p[1]-upperfit_p[1])/(upperfit_p[0]-lowerfit_p[0])
    yc=np.polyval(lowerfit_p,xc)

    #get 'knee'
    #rr=np.hypot((1:length(sim))-xc).'.^2, (sim-yc).^2);
    rr=np.hypot(pix_ax-xc,impixels_sorted-yc)
    x_kn=pix_ax[(rr== min(rr))]
    y_kn=impixels_sorted[(rr== min(rr))]
    #scale value back
    treshold=y_kn/Npix*Ipix

    im_BW=(im>treshold)*1.0
    im_tres=(im>treshold)*im

    return im_tres, im_BW


def track_radial_pattern(roi, runmodus=1, x0=0, y0=0, mapradius=0, demo=1):
    """ perform QI-based tracking 
    runmodus 0 = just map using x0 and y0
    runmodus 1 = same, export final data
    """
    roi_array = np.array(roi)  #for tracking                
    # QI_track on one channel, standard radius
    rr=np.shape(roi)[0]
    if runmodus==0:
        r0=mapradius
    else:
        r0=rr/2
    QI=QI_Tracker(roi_array)
    preset=QI_Tracker.TrackXY_by_QI_Init(QI,roi_array) 
    
    if runmodus == 0:
        #single run, forced mapping:
        preset['maxradius']=mapradius
        preset['iterations']=2
        x_in = x0
        y_in = y0
    if runmodus == 1:
        #iterative tracking:
        x_in = rr/2
        y_in = rr/2
    xq, yq, allprofiles = QI_Tracker.TrackXY_by_QI(QI,roi_array, preset, x_in, y_in)    
    
    if demo:
        fig, axs = plt.subplots(1,2)
        plotgridy=preset["X0samplinggrid"]+xq
        plotgridx=preset["Y0samplinggrid"]+yq
        axs[0].imshow(roi)
        lx=np.shape(plotgridx)
        axs[0].plot(plotgridx[::10,::20],plotgridy[::10,::20],'r-',linewidth=0.3)
        axs[0].set_title('tracked by QI') 
        axs[1].imshow(allprofiles)
        axs[1].set_title('polar map') 
        fig.tight_layout()
        
        return fig,axs
    else:
        if runmodus ==1: return xq, yq, allprofiles
        if runmodus ==0: return x_in, y_in, allprofiles

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

def smooth_it(roi,labda=3):
    #gaussian smooth
    roi = roi.astype(float)
    k_size=np.int(np.ceil(labda))
    x, y = np.linspace(-k_size, k_size, 2*k_size), np.linspace(-k_size, k_size, 2*k_size)
    KX, KY = np.meshgrid(x, y)
    radii = np.hypot(KX, KY)
    kernel1=np.exp(-(radii)/(2**0.5*labda))
    kernel1=kernel1/np.sum(kernel1)
    #kernel1 = np.ones((k_size, k_size), np.float32)/(k_size**2)
    roi_smz = cv2.filter2D(src=roi, ddepth=-1, kernel=kernel1) 
    if 0: #test
        fig, axs = plt.subplots(1,1)
        axs.imshow(roi_smz)
        fig.tight_layout()
        fig.show()
        dum=1
    return roi_smz

def sobel_it(roi):  
    # apply kernel(2d convolution matrix
    sobel_h = sobel(roi, 0)  # horizontal gradient
    sobel_v = sobel(roi, 1)  # vertical gradient
    magnitude = np.sqrt(sobel_h**2 + sobel_v**2)
    magnitude=np.array(magnitude.astype(int))
    #magnitude *= 255.0 / np.max(magnitude)  # normalization
    if 0: #test
        fig, axs = plt.subplots(1,1)
        axs.imshow(roi)
        fig.tight_layout()
        fig.show()
        dum=1
    return magnitude

def donut_mask_it(roi):
    """
    make donut-shaped mask to improve QI tracking of versicle edge.
    Note: we assume a roi is taken as 3 times the approximate vesicle diameter (thus, we expet the vesicle edge at about 2/3* half the image size)
    @author: jkerssemakers, 2024
    """
    rr,cc =np.shape(roi)
    approx_rim=rr/4  
    rim_lo=0.1*approx_rim
    rim_hi=1.3*approx_rim
    rim_sharpness=rr/40
    x, y = np.linspace(-cc / 2, cc / 2, cc), np.linspace(-rr / 2, rr / 2, rr)
    X, Y = np.meshgrid(x, y)
    radii = np.hypot(X, Y)
    donut_mask=0*radii+1
    #smooth band:
    if 1:
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
        axs.imshow(donut_mask)
        #axs.plot(donut_mask)
        fig.tight_layout()
        fig.show()
        dum=1

    return roi_out
