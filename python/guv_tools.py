""" #guv_tools
#tools to work with guv files: """
import numpy as np
import matplotlib.pyplot as plt
import math as mt
#import nd2reader
#from readlif.reader import LifFile
from pathlib import Path
import cv2
import csv
from skimage import io
from scipy.ndimage import sobel
from scipy.ndimage import map_coordinates             # for converting cartesian to circular coördinates in QI
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

def get_xy_contour(edge_map, presets):
    # get a smooth xy contour from polar coordinates
    # assume an egde running through a polar map. 
    labda=3    
    edge_map=smooth_it(edge_map,labda)
    mnr=presets["minradius"]
    mxr=presets["maxradius"]
    cr=presets["radialoversampling"]
    rr, cc = np.shape(edge_map)
    #get maximum in polar map
    max_I_idx=[]
    for ci in np.arange(cc):
        col = [rw[ci] for rw in edge_map]
        if sum(col)>0:
            max_I_idx.append(np.argmax(col))
        else:
            max_I_idx.append(np.nan)

    # to do: get a smoothend dependence or a fit
    #HERE 


    #translate back to xy:
    true_radius=(mnr+np.array(max_I_idx))/cr
    true_angle=np.linspace(0,2*mt.pi, len(true_radius))
    true_x = []
    true_y = []
    for r,a in zip(true_radius, true_angle):
        true_x.append(r*mt.cos(a))
        true_y.append(r*mt.sin(a))
    #close contour:
    true_x.append(true_x[0])
    true_y.append(true_y[0])    
    true_x=np.array(true_x)
    true_y=np.array(true_y)
    #smooth with com, if there are no gaps:
    if (len(np.argwhere(np.isnan(true_radius))))==0:
        true_x,true_y, alpha=smooth_lines(true_x, true_y, labda, demo=0)      
        if 0:
            fig, axs = plt.subplots(1,1)
            axs.plot(true_x,true_y,'ro-')
            fig.show()
    return true_x, true_y

def measure_perimeter(true_x, true_y):
    #measure perimater and average radius of smooth contour
    if (len(np.argwhere(np.isnan(true_x))))==0:
        LC=np.sum((np.diff(true_x)**2+(np.diff(true_y)**2)**0.5))
        mnx=np.nanmean(true_x)
        mny=np.nanmean(true_y)
        true_radius=((true_x-mnx)**2+(true_y-mny)**2)**0.5
        RC=np.nanmean(true_radius)
        LR=2*mt.pi*RC
    else:
        LC=np.nan
        LR=np.nan
        RC=np.nan
    return LC, LR, RC

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
        if runmodus ==1: return xq, yq, allprofiles,preset
        if runmodus ==0: return x_in, y_in, allprofiles, preset


def QI_map(im, QI, x0, y0):
    #condensed QI mapping
    #With this function a radial sampling grid, based on the size of the image, is built.
    spokesnoperquad=np.ceil(2*np.pi*QI['maxradius']*QI['angularoversampling']/4) #The reverse of np.floor. np.ceil rounds the coordinates to the nearest integer higher or equal to that element, for example 2.4 becomes 3 and -3.4 becomes -3.0
    radbinsno=(QI['maxradius']-QI['minradius'])*QI['radialoversampling']
    angles= np.linspace(-(1/4)*np.pi,(7/4)*np.pi, int(4*spokesnoperquad +1)) #The angles are set in a linspace ranging from -π/4 to 7/4*π, with steps a number of spokesnoperquad*4+1 steps
    angularstep=np.pi/2/spokesnoperquad #This is the step size of the angles
    angles=angles[0:-2]+angularstep/2 #Center the angles per quadrant
    radbins=np.linspace(QI['minradius'],QI['maxradius'],int(radbinsno)) #Linspace ranging from QI.minradius to QI.maxradius with a number of radbinsno steps
    [argsgrid,radiigrid]=np.meshgrid(angles,radbins) #Here coordinate matrices are returned from coordinate vectors
    QI['Y0samplinggrid']=(radiigrid*np.sin(argsgrid)) #Here the Y grid is created
    QI['X0samplinggrid']=(radiigrid*np.cos(argsgrid)) #Here the X grid is created
    QI['angles']=angles
    QI['radbii']=radbins

    Xsamplinggrid=QI['X0samplinggrid']+x0 #The grid is made with the Samplinggrid made in the function above
    Ysamplinggrid=QI['Y0samplinggrid']+y0

    allprofiles = map_coordinates(im, [Xsamplinggrid.ravel(), Ysamplinggrid.ravel()], order=3, mode='nearest').reshape(Xsamplinggrid.shape) #This function does the same as interp2, it interpolates the 2D gridded data in meshgrid format
    
    return allprofiles

def check_limits(x0,y0, dims):
    in_range=True
    if (x0<0) or (x0 >= dims[0]) or (y0<0) or (y0 >= dims[1]):
        in_range=False
    return in_range


def get_roi(image,x0,y0,r0):
    """
    basic collection of points
    'image' can also be a stack
    @author: jkerssemakers, 2024
    """
    #cuts square area with inscribed radius r0. 
    # If outside-FOV, roi is shifted
    dims =np.shape(image)
    #force roi size:

    roi = np.zeros((2*r0,2*r0))
    if check_limits(x0,y0, dims):
        lox=int(max([0, x0 - r0]))
        hix=int(min([dims[0], x0+r0]))
        loy=int(max([0, y0 - r0]))
        hiy=int(min([dims[1], y0+r0]))

        if len(dims)==2:
            roi[0:hiy-loy, 0:hix-lox] = image[loy:hiy, lox:hix]
        if len(dims)==3:
            roi[0:hiy-loy, 0:hix-lox] = image[loy:hiy, lox:hix,:]

    return roi

def highlight_roi(image,x0,y0,r0):
    """
    @author: jkerssemakers, 2024
    """
    #showss square area with inscribed radius r0. 
    # If outside-FOV, roi is shifted
    dims =np.shape(image)
    #force roi size:
    image_roi=1*image
    
    roi = np.zeros((2*r0,2*r0))
    if check_limits(x0,y0, dims):
        lox=int(max([0, x0 - r0]))
        hix=int(min([dims[0], x0+r0]))
        loy=int(max([0, y0 - r0]))
        hiy=int(min([dims[1], y0+r0]))

        if len(dims)==2:
            roi[0:hiy-loy, 0:hix-lox] = image[loy:hiy, lox:hix]
        if len(dims)==3:
            roi[0:hiy-loy, 0:hix-lox] = image[loy:hiy, lox:hix,:]
        mxr=np.max(roi)
        image_roi[loy:hiy, lox]=0.9*mxr
        image_roi[loy:hiy, hix-1]=0.9*mxr
        image_roi[loy, lox:hix]=0.9*mxr
        image_roi[hiy-1, lox:hix]=0.9*mxr

    return image_roi

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

def soft_mask_it(roi):
    """
    make donut-shaped mask to improve QI tracking of versicle edge.
    Note: we assume a roi is taken as 2 times the approximate vesicle diameter 
    @author: jkerssemakers, 2024
    """
    rr,cc =np.shape(roi)
    approx_rim=rr/4  
    rim_lo=0.1*approx_rim
    rim_hi=1.7*approx_rim
    rim_sharpness=rr/40
    x, y = np.linspace(-cc / 2, cc / 2, cc), np.linspace(-rr / 2, rr / 2, rr)
    X, Y = np.meshgrid(x, y)
    radii = np.hypot(X, Y)
    donut_mask=0*radii+1
    #smooth band:
    if 1:
        #donut_mask[radii<rim_lo]=0
        donut_mask[radii>rim_hi]=0
        rimsmooth_lo=1-np.exp(-(radii-rim_lo)/rim_sharpness)
        rimsmooth_hi=1-np.exp(-(rim_hi-radii)/rim_sharpness)
        donut_mask=donut_mask*rimsmooth_hi
        roi_out=roi*donut_mask
    if 0: #test
        fig, axs = plt.subplots(1,1)
        axs.imshow(donut_mask)
        #axs.plot(donut_mask)
        fig.tight_layout()
        fig.show()
        dum=1

    return roi_out

def make_montage(tiff_in, format_out='tiff'):
    """ from a single t (or z) stack, build a montage for evaluation purposes """
    fovs,rr,cc =np.shape(tiff_in)
    sz_h= int(np.ceil(fovs**0.5))
    if ((sz_h-1)*sz_h)>=fovs:
        sz_v=sz_h-1
    else:
        sz_v=sz_h
    first_fov=np.log((0*tiff_in[0]+1))
    mxval=np.max(first_fov)
    montage_tiff=np.tile((0*first_fov+mxval),(sz_v,sz_h))
    for ix, fov in enumerate(tiff_in):
       
        col_i=int(np.mod(ix,sz_h))
        rw_i=int(np.floor(ix/sz_h))
        lox=col_i*cc
        hix=lox+cc
        loy=rw_i*rr
        hiy=loy+rr
        montage_tiff[loy:hiy,lox:hix]=np.log(fov+1)
        t=np.log(fov+1)
        if 0:
            fig, ax = plt.subplots(1, 2)
            ax[0].imshow(montage_tiff)
            fig.show()
            dum=1
    if format_out == 'tiff':
        return montage_tiff
    
def smooth_lines(xx, yy, r0, demo=0):
    """
    Smooth a noise collection of xy points with local com.
    """
    # demo section start ------------------------
    if demo:
        pts = 200
        imsz = 200
        xx = np.linspace(10, imsz - 10, pts)
        yy = imsz / 2 * (1 + 0.25 * np.random.rand(pts)) + imsz / 3 * np.sin(
            xx / imsz * 2 * math.pi
        )
        r0 = imsz / 20
    # demo section stop  ------------------------
    Ls = len(xx)
    xx_s = 0 * xx
    yy_s = 0 * yy
    alpha = 0 * xx
    for ii in np.arange(Ls):
        x0 = xx[ii]
        y0 = yy[ii]
        xx_near, yy_near, rn_near = get_nearby(x0, y0, xx, yy, r0)
        # use 1-normalized radius as weight
        zz = 1 - rn_near  # weights
        xm, ym, alfa, ecc = get_com_extra(xx_near, yy_near, zz, use_weights=1)
        xx_s[ii] = xm
        yy_s[ii] = ym
        alpha[ii] = alfa
    # demo section start ------------------------
    if demo:
        plt.plot(xx, yy, "o", markersize=5)
        plt.plot(xx_s, yy_s, "ro", markersize=3)
        plt.show()
    # demo section stop  ------------------------
    return xx_s, yy_s, alpha

def get_com_extra(xx, yy, zz, use_weights, demo=0):
    """
    Central angular moments of a collection of points (xx,yy,zz)
    'zz' can serve as weight of not
    from: http://en.wikipedia.org/wiki/Image_moment
    JacobKers MatLab 2012 --> Python 2021
    """
    # demo section starts here ------------------------
    if demo:
        use_weights = 1
        n = 200
        xx = np.random.rand(n, 1)
        yy = -3 * xx + 0.1 * (np.random.randn(n, 1) - 0.5)
        zz = np.random.rand(n, 1)
    # demo section stop  ------------------------
    if use_weights == 0:  # no weights
        zz = 0 * zz + 1
    # raw moments M_ij of points: Mij=sum(x^i*y^j*Ixy)
    M00 = np.sum(zz)
    M10 = np.sum(xx * zz)
    M11 = np.sum(yy * xx * zz)
    M01 = np.sum(yy * zz)
    M20 = np.sum((xx**2) * zz)
    M02 = np.sum((yy**2) * zz)
    # Centroid row and column
    xm = M10 / M00
    ym = M01 / M00
    #   Second order central moments
    mu_prime20 = M20 / M00 - xm**2
    mu_prime02 = M02 / M00 - ym**2
    mu_prime11 = M11 / M00 - xm * ym
    #   theta=0.5*atan(2*mu_prime11/(mu_prime20-mu_prime02))*180/pi;
    at_y = mu_prime20 - mu_prime02
    at_x = 2 * mu_prime11
    theta = 0.5 * 180 / mt.pi * np.arctan2(at_x, at_y)

    # eigenvalues covariance matrix:
    labda1 = (
        0.5 * (mu_prime20 + mu_prime02)
        + 0.5 * (4 * mu_prime11**2 + (mu_prime20 - mu_prime02) ** 2) ** 0.5
    )
    labda2 = (
        0.5 * (mu_prime20 + mu_prime02)
        - 0.5 * (4 * mu_prime11**2 + (mu_prime20 - mu_prime02) ** 2) ** 0.5
    )
    # eccentricity
    ecc = (1 - labda2 / labda1) ** 0.5
    # demo section start ------------------------
    if demo:
        plt.plot(xx, yy, "ro")
        plt.show()
    # demo section stop  ------------------------
    return xm, ym, theta, ecc

def get_nearby(x0=1, y0=1, xx=1, yy=1, r0=1, demo=0):
    """
    Find selection of points near a given point.
    Normalized distance is also exported, for example to be used as weight.
    """
    # demo section start ------------------------
    if demo:
        r0 = 1
        x0 = 0.5
        y0 = 0
        use_weights = 1
        pts = 200
        xx = np.random.randn(pts, 1)
        yy = np.random.randn(pts, 1)
        points = np.concatenate((xx, yy), axis=1)
    # demo section stop  ------------------------
    rn = np.hypot(xx - x0, yy - y0) / r0
    ix = np.array(np.argwhere(rn < 1))

    xx_near = xx[ix[:, 0]]
    yy_near = yy[ix[:, 0]]
    rn_near = rn[ix[:, 0]]
    # demo section start ------------------------
    if demo:
        plt.plot(xx, yy, "o")
        plt.plot(xx_near, yy_near, "ro")
        plt.plot(x0, y0, "ko", markersize=10)
        plt.show()
    # demo section stop  ------------------------
    return xx_near, yy_near, rn_near

