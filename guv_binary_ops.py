# -*- coding: utf-8 -*-
"""
examples of binary operations 
@author: jkerssemakers
other info:
# https://www.geeksforgeeks.org/image-segmentation-using-morphological-operation/
# https://docs.opencv.org/3.3.1/d3/db4/tutorial_py_watershed.html
"""
import math as mt
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
from skimage.morphology import ball, disk, square, diamond, ball
from skimage.draw import polygon2mask
from scipy.ndimage import binary_opening, binary_closing, binary_fill_holes, binary_dilation, binary_erosion
from scipy.signal import savgol_filter

def mask_central_object(im_fg):
    """Keep only central object in 2D boolean mask, M. Holub '23?
    Args:
        im (np.ndarray): boolean mask to use
    Returns:
        im_fg (bool np.ndarray): foreground mask
        im_bg (bool np.ndarray): background mask
    """
    centr = [int(x/2) for x in im_fg.shape]
    labels, n_labels = measure.label(im_fg, return_num = True)
    regprops = measure.regionprops(labels)

    if n_labels > 1: # 0,1 are there always if some bg found, but 0 does not count towards n_labels
        # index of biggest region
        #idx = np.argmax([l.area for l in regprops])

        #idx of region closest to center.
        centrs = [l.centroid for l in regprops]
        idx = np.argmin(np.sum((np.array(centr)-np.array(centrs)) ** 2, axis = 1))

        # create mask with a single label
        im_fg = np.zeros_like(im_fg, dtype = 'bool')
        im_fg[labels == regprops[idx].label] = True

    im_bg = ~im_fg
    return im_fg, im_bg

def sorted_pixels_treshold(im):
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
    if isinstance(treshold, np.ndarray):
        treshold=treshold[0]
    msk=im>treshold
    spot_tres=msk*im
    return spot_tres, msk, treshold 

