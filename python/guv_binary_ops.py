# -*- coding: utf-8 -*-
"""
examples of binary operations 
@author: jkerssemakers
other info:
# https://www.geeksforgeeks.org/image-segmentation-using-morphological-operation/
# https://docs.opencv.org/3.3.1/d3/db4/tutorial_py_watershed.html
"""

import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
from skimage.morphology import ball, disk, square, diamond, ball
from skimage.draw import polygon2mask
from scipy.ndimage import binary_opening, binary_closing, binary_fill_holes, binary_dilation
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


def binary_actions(im):
    """ examples of binary image operations, re-edited from M.Holub'24 
    MH sequence default ON is labeled with (1)"""
    #ignore nans:
    if 0: im = np.ma.masked_where(np.isnan(im), im) 
    #simple treshold:
    if 0: fgm = im>0.2*(np.max(im) -np.mean(im)) + np.mean(im)
    # triangulation treshold:
    if 1: fgm=sorted_pixels_treshold(im)[1]
    # remove tiny regions:
    if 0: fgm = binary_opening(fgm, disk(3), iterations = 2)
    # connect fragmented regions:
    if 1: fgm = binary_closing(fgm, diamond(5)) 
    # remove small regions:
    if 0: fgm = binary_opening(fgm, disk(5))
    # close dark holes:
    if 1: fgm = binary_closing(fgm, square(3))
    # more filling:
    if 1: fgm = binary_fill_holes(fgm, square(3))
    # pick largest object:
    if 1: fgm = mask_central_object(fgm)[0]
    #dilate(1)
    if 0: fgm = binary_dilation(fgm, disk(3), iterations = 4)
    # fill holes in mask (1)
    if 1: fgm = binary_fill_holes(fgm)
    # smooth boundary(1)
    if 1 and fgm.sum() > 0: 
        fgm = smooth_boundary(fgm)  
    #some more dilation (1)
    if 0: 
        try:
            fgm = binary_dilation(fgm, ball(3), iterations = 1)
        except Exception as e:
            print("planar_masking.binary_dilation: 3D Dilating with diamond")
            fgm = binary_dilation(fgm, iterations = 1)

    return fgm

def smooth_boundary(mask):
    """Smooth mask boundary by applying Savitzky Golay Filter

    You will have to close all holes before applying the filter.

    Returns:
        mask (np.ndarray): smoothed mask

    References:
        # https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.find_contours
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html
        # https://bartwronski.com/2021/11/03/study-of-smoothing-filters-savitzky-golay-filters/
    """

    try:
        bnd = measure.find_contours(mask)[0]
    except IndexError as e: # not sure why this happens if fgm.sum()>0
        return mask
    # boundary smoothing produces corrupt mask if mask on the edge already
    # maybe can fix this with using different 'mode'
    touches_edge = (np.logical_or(bnd.flatten() == 0, bnd.flatten() >= (mask.shape[0]-1))).sum()
    if touches_edge: return mask

    bnd_length = len(bnd)
    # MH: parameters here are somewhat arbitrary - works quite well with range of params
    win_length = bnd_length // 4
    if not np.mod(win_length, 2): win_length += 1 # most be odd
    savgol_params = {'polyorder': 8, 'mode': 'interp'}

    if win_length > 7:
        #x_out = savgol_filter(np.repeat(bnd[:, 0], 2), win_length, **savgol_params)
        #y_out = savgol_filter(np.repeat(bnd[:, 1], 2), win_length, **savgol_params)
        #bnd_smooth = np.asarray([x_out[:bnd_length], y_out[:bnd_length]]).T

        x_out = savgol_filter(bnd[:, 0], win_length, **savgol_params)
        y_out = savgol_filter(bnd[:, 1], win_length, **savgol_params)
        bnd_smooth = np.asarray([x_out, y_out]).T
        # convert list of points to a closed boolean shape
        mask = polygon2mask(mask.shape, bnd_smooth)
    return mask

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
    msk=im>treshold
    spot_tres=msk*im
    return spot_tres, msk, treshold 

def generate_spot(
    psf=2,  # point spread
    size=150,  # image size (square shape)
    amplitude=1,  # amplitude
    SN_ratio=0.06,  # signal/noise ratio
    node_x=0,  # relative center position of the spot (0=center)
    node_y=0,  # relative center position of the spot (1=edge)
):
    """
    This generates a spot for quick testing.
    coordinates image run from -10 to 10
    """
    x, y = np.linspace(-10 - node_x * 10, 10 - node_x * 10, size), np.linspace(
        -10 - node_y * 10, 10 - node_y * 10, size
    )
    X, Y = np.meshgrid(x, y)
    rr = np.hypot(X, Y)
    frame = amplitude * np.exp((-(rr/ (2*psf))** 2))
    noise = SN_ratio * amplitude * np.random.randn(size, size)
    spot_im = frame + noise

    return spot_im


def  work_binaries(roi_tr):
    BW_edge=0*roi_tr
    msk = binary_actions(roi_tr)
    labels, n_labels = measure.label(msk, return_num = True)
    regprops = measure.regionprops(labels)
    if len(regprops)>0:
        xc,yc = regprops[0].centroid
        if 0: #test
            plt.close('all')
            fig, axs = plt.subplots(1,2)
            axs[0].imshow(roi_tr)
            axs[1].imshow(msk)
            axs[1].plot(xc,yc, 'ro')
            #axs.plot(donut_mask)
            fig.tight_layout()
            fig.show()
            dum=1
            plt.close('all')
        else:
            xc = []
            yc = []
        
    return  msk, BW_edge, xc, yc 


# show:
badcodinghabit = 0
if badcodinghabit:
    spotim=generate_spot(node_x=0.3,node_y=0.3,psf=2,amplitude=1) + generate_spot(node_x=-0.3,node_y=-0.3,psf=1) + generate_spot(psf=1)
    msk = binary_actions(spotim)
    fig, axs=plt.subplots(1,2)
    axs[0].imshow(spotim)
    axs[1].imshow(msk)
    fig.show()
    axs[0].set_title("spot")
    fig.tight_layout()
    print("Press any key to end demo")
    input()
    plt.close("all")
