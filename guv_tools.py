""" #guv_tools
#tools to work with guv files: """
#customs:


import numpy as np
import math as mt
#import nd2reader
#from readlif.reader import LifFile
import cv2
from scipy.optimize import curve_fit
from scipy.ndimage import sobel
from scipy.ndimage import map_coordinates   # for converting cartesian to circular coördinates in QI
import matplotlib.pyplot as plt

def outlier_flag(data=0, tolerance=2.5, sig_change=0.7, how=1, sho=1, demo=0):
    """
    An iterative tool to separate a distribution from its outliers.
    An initial estimate of average 'mu' and standard deviation 'sigma' is used to identify outliers.
    These are removed and [mu,sigma] is re-determnined] after wchich the sequence is repeated
    until sigma does not change much anymore
    Input:
        data: single array of values
        tolerance: outliers are points more than [tolerance] standard deviations away from the average.
        sigchange: iteration stops if sigma is changed less than a fraction  'sigchange'.
        how
    sho
    demo
    Output:
        1) array of outliers
        2) array of inliers
        3) flags: binary trace indicating which points where outliers in the original data.
    Jacob Kers '2022
    """
    # demo section start ------------------------
    if demo:
        # build trace with 2 distributions
        N_pts = 2000
        s1 = 10
        u1 = 0
        N_otl = 200
        s2 = 10
        u2 = 100
        temp_ax = np.arange(0, N_pts, 1)
        data = s1 * np.random.randn(N_pts, 1) + u1
        for ii in range(N_otl):
            randii = int((N_pts - 1) * np.random.rand(1, 1))
            data[randii] = s2 * np.random.randn(1, 1) + u2
    # demo section stop  ------------------------

    sig_ratio = 0
    sigma_nw = 1e20
    flags = 0 * data + 1
    inliers=data
    outliers=[]
    while sig_ratio < sig_change:
        sigma_old = sigma_nw
        ix_in = np.ndarray.nonzero(flags == 1)
        ix_out = np.ndarray.nonzero(flags == 0)
        inliers = data[ix_in]
        outliers = data[ix_out]
        #health check:
        av = safe_median(inliers)
        sigma_nw = safe_std(inliers)
        sig_ratio = sigma_nw / sigma_old
        if how == 1:
            flags = (data - av) < tolerance * sigma_nw
        elif how == 0:
            flags = abs(data - av) < tolerance * sigma_nw
        elif how == -1:
            flags = (data - av) > -tolerance * sigma_nw
        if sho:
            lo = np.min(inliers)
            hi = np.max(inliers)
            bins = np.linspace(lo, hi, 40)
            fig2, ax2 = plt.subplots(1, 1)
            plt.hist(inliers, bins, histtype="bar")
            plt.show()
            dum = 1

    return inliers, outliers, flags

def sine_function(x, A, C):
    """
    Sine function with fixed period (equal to half the trace length) and phase 0.
    
    Parameters:
    x : array-like
        The x values
    A : float
        Amplitude of the sine wave
    C : float
        Vertical offset
    
    Returns:
    y : array-like
        The y values of the sine wave
    """
    return A * np.sin(2 * np.pi * x / (0.5*len(x))) + C

def fit_sine_to_trace(x_data,y_data):
    """
    Fit a sine wave to the given data trace.
    
    Parameters:
    y_data : array-like
        The y values of the data trace
    
    Returns:
    popt : array
        Optimal values for the parameters (A, C)
    pcov : 2D array
        The estimated covariance of popt
    """
    
    # Initial guess for the parameters
    A_guess = (np.max(y_data) - np.min(y_data)) / 2
    C_guess = np.mean(y_data)
    p0 = [A_guess, C_guess]
    
    # Fit the function
    popt, pcov = curve_fit(sine_function, x_data, y_data, p0=p0)
    
    return popt, pcov


def QI_map(im, QI, x0, y0, demo=0):
    #condensed QI mapping
    #With this function a radial sampling grid, based on the size of the image, is built.
    spokesnoperquad=np.ceil(2*np.pi*QI['maxradius']*QI['angularoversampling']/4) #The reverse of np.floor. np.ceil rounds the coordinates to the nearest integer higher or equal to that element, for example 2.4 becomes 3 and -3.4 becomes -3.0
    #spokesnoperquad=90
   
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

    allprofiles = map_coordinates(im, [Xsamplinggrid.ravel(), Ysamplinggrid.ravel()], order=3, mode='nearest').reshape(Xsamplinggrid.shape) 
    #This function does the same as interp2, it interpolates the 2D gridded data in meshgrid format
    if demo == 0:
        return allprofiles
    else:
        return allprofiles, QI, Xsamplinggrid, Ysamplinggrid



def smooth_it(roi,labda=3):
    #gaussian smooth
    roi = roi.astype(float)
    k_size=int(np.ceil(labda))
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


def safe_mean(data):
    if data.size == 0:
        return np.nan
    return np.mean(data)

def safe_median(data):
    if data.size == 0:
        return np.nan
    return np.median(data)

def safe_std(data):
    if data.size == 0:
        return np.nan
    return np.std(data)

def subpix_step(ys): #This function calculates a sub pixel step of a local maximum
        #This is achieved with again a parabolic fitting
        xs=np.arange(-1,2)#Here an array is made from 0 to the value of ld
        if np.max(ys)>np.min(ys) and len(ys)==3:
            prms=np.polyfit(xs,ys,2)#Here the location is polyfitted
            x=-prms[1]/(2*prms[0])
            ft=np.polyval(xs,prms)
        else:
            x=np.nan
            ft=np.nan
        return x