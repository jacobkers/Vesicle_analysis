
################################################################################################################################
## Libraries

import numpy as np                                    # for arrays and math
from PIL import Image                                 # for opening and analysing images

import matplotlib.pyplot as plt                       # for plots and visualisation
from matplotlib.figure import Figure                  # Figure instead of plt.figure so plots don't show inline, but only in the GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # for making figures in the GUI. Bridge between matplotlib and tkinter
# This librarie and the function that uses it only works in the ipynb file format (jupyter lab/notebook)
#from IPython.display import clear_output              # for animation of .tif file

from tkinter.filedialog import askopenfilename        # for creating a file browser window
from scipy.ndimage import map_coordinates             # for converting cartesian to circular coördinates in QI
from scipy.optimize import curve_fit                  # for spectral method fit (trap constant)
from scipy.interpolate import interp2d                # for creating an interpolated, continuous function from discrete data

from warnings import warn                             # for creating warnings if needed
from os.path import splitext, basename, isfile        # for analysing name and extension of a chosen file
import time                                           # for keeping track of time


##############################################################################################################################
### Quadrant Interpolation (QI) Tracking

'''
QI Tracker
Created on Thu Apr 23 14:44:46 2020

@authors: 
- Jasper van der Gronde, Fenna Timsi (class (OOP), init)
'''

# The QI tracker is defined as a class, since the utility is a set of related variables and functions.
class QI_Tracker():
    # -------------------------------------------------------------------------------------------
    # QI Tracker Class Object.
    # For more information j.h.h.vandergronde@student.tudelft.nl
    # -------------------------------------------------------------------------------------------
    # CLASS ATTRIBUTES WHICH WILL BE STORED IN THE OBJECT.
    # IT CAN SIMPLY BE CALLED WITH self.attr INSIDE THE CLASS FUNCTIONS
    # OUTSIDE IT CAN ALSO BE CALLED, BUT NOW FROM THE OBJECT NAME (SEE EXAMPLE).
    # WHEN INITIALIZING THE OBJECT THEY CAN BE OVERWRITTEN BY SETTING THEM AS KEYWORD ARGUMENTS.
    # -------------------------------------------------------------------------------------------
    image = 0                # numpy ndarray - contains the (first) image data
    
    radialoversampling = 2.0 # float - over-sampling of radial bins
    angularoversampling = 0.7# float - over-sampling of angular spokes
    
    minradius = 0.0          # float - minimum radius of polar grid
    maxradius = 0.0          # float - maxiumum radius of polar grid
    max_radius_denom = 2.5   # By default 2.5, but should be able to be changed in the init function as kwarg.
    
    iterations = 10          # integer - no. of iterations
    spokesnoperquad = 0      # integer - no. of spokes per quadrant 
    radbinsno = 0            # integer - no. of radial bins
    radbins = 0              # numpy ndarray - linear space containg radii
    angles = 0               # numpy ndarray - linear space containing angles
    angularstep = 0.0        # float - angilar step size
    
    argsgrid = 0             # numpy ndarray - grid containing angles
    radiigrid = 0            # numpy ndarray - grid containing radii
    X0samplinggrid = 0       # numpy ndarray - x coordinates from the sampled polar grid
    Y0samplinggrid = 0       # numpy ndarray - y coordinates from the sampled polar grid
    
    
    # This function initialize the QI_Tracker object which is called with:
    # var = QI_Tracker(image)
    def __init__(self, im, **kwargs):
        """
        Initializes the QI tracker class and returns the object.        
    
        Arguments:
        I -- Numpy 2D array of a random frame of the image

        Keyword arguments:
        radialoversampling
        angularoversampling
        minradius
        maxradius
        iterations
        ... and many other other attributes that are defined in the class.
        
        """
        assert 'np' in globals(), "numpy must be imported at the beginning of the file as np."
        assert 'plt' in globals(), "matplotlib.pyplot must be imported at the beginning of the file as plt."
        assert type(im) is list or type(im) is np.ndarray, "Image must be of type list or ndarray"
        assert len(im) > 0, "Image cannot be empty"
    
        # convert to numpy array if list is given.
        if type(im) is not np.ndarray: 
            im = np.array(im)
        
        self.frame = im
            
        # Override the default class attributes from the keyword arguments
        # Condition: Only if they exist in the class.
        for arg, val in kwargs.items(): 
            if arg in dir(self): setattr(self, arg, val)
        
        # -------------------------------------------------------------------------------------------
        # Creating the polar grid.
        # -------------------------------------------------------------------------------------------
        # Define the max-radius of the polar grid.
        self.maxradius = np.min(self.frame.shape)/self.max_radius_denom
        # The no. of radial bins is defined as (r_max - r_min) x over-sampling.
        # int(...) <--> Solves warning cannot safely be interpretated as integer.
        self.radbinsno = int((self.maxradius - self.minradius) *self.radialoversampling)
        # Generate a linear space of radii, with the sampling given by radbinsno.
        self.radbins = np.linspace(self.minradius, self.maxradius, self.radbinsno)
        # The no. of spokes per quadrant is defined as .5πr_max x over-sampling (in this case under-sampling)
        # int(...) <--> Solves warning cannot safely be interpretated as integer.
        self.spokesnoperquad = int(np.ceil( (1/2) *np.pi *self.maxradius *self.angularoversampling))
        # From the no. of spokes per quadrant compute the angles in an array with a linear space.
        # Start at -π/4 and end at the same location 7π/4.
        # The total number of points then becomes 4 times the no. of spokes per quadrant +1 (including zero)
        self.angles = np.linspace(-(1/4)*np.pi,(7/4)*np.pi, 4*self.spokesnoperquad +1) 
        # Define the angular step size, can also with self.angles[1] - self.angles[0]
        self.angularstep = np.pi/(2*self.spokesnoperquad)
        # Center the angles. 
        self.angles = self.angles[1:-1] + self.angularstep/2
        # Generate a 2D grid containing the angles (args) and radii.
        self.argsgrid, self.radiigrid = np.meshgrid(self.angles, self.radbins)
        # Create X,Y coords from the polar grid.
        self.X0samplinggrid = self.radiigrid*np.cos(self.argsgrid)
        self.Y0samplinggrid = self.radiigrid*np.sin(self.argsgrid)
        return None
    
    """
    Finalized on Wed January 20 16:00 2021

    @author: Folkert Straus and Isa Veeneman
    """
    
    def Build_QI_SamplinggridGrid(self,QI):
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
        return QI
    
    def TrackXY_by_QI_Init(self,firstim):
        pretracksettings={#
            'oversampling' : 2,#The radiaoversampling is set to two
            'angularoversampling' : 0.7,#The angular oversampling is set to 0.7
            'radialoversampling' : 2, #ROMAN:I PUT A RANDOM VALUE HERE
            'minradius' : 0,#the minimal radius is 0
            'maxradius' : np.amin(np.shape(firstim))/2.5,#The maximum radius
            'iterations' : 10,#The calculation of the center is repeated 10 times, the more the better however if it takes too long it can be turned down but the minimum is 5
        }
        pretracksettings=self.Build_QI_SamplinggridGrid(pretracksettings) #This calculates the relative coordinates of the radial sampling grid, it is done beforehand because that takes less time.
        return pretracksettings
    
     
    # This function corresponds to the main function TrackXY_by_QI in the mathlab file    
    def TrackXY_by_QI(self,im, QI, xm, ym):            
            QI['radialoversampling']=2 #These settings are also defined above, but for certainty there are also defined in thsi definition
            QI['angularoversampling']=0.7
            QI['minradius']=0
            QI['maxradius']=50/3
            QI['iterations']=10
            QI=self.TrackXY_by_QI_Init(im)
            
            xnw=xm
            ynw=ym
            
            errx=np.zeros((QI['iterations'],1))
            prequit=0
        #This is the iterative section to improve the tracking, it is done 10 times because otherwise it will take too long
            for ii in range(1,QI['iterations']):#This means it is doing 1 to 10 iterations, this can be altered by changing QI.Iterations
                if not prequit:
                    xol=xnw #This sets the location
                    yol=ynw
                    Xsamplinggrid=QI['X0samplinggrid']+xnw #The grid is made with the Samplinggrid made in the function above
                    Ysamplinggrid=QI['Y0samplinggrid']+ynw
                    NewXsamplinggrid = Xsamplinggrid[:,0]#Here a vertical array is made with all the values
                    NewYsamplinggrid = Ysamplinggrid[:,0]
                    sz = im.shape
                    x = np.arange(0, sz[1])
                    y = np.arange(0, sz[0])
                    f = interp2d(x,y,im)
                    allprofiles = map_coordinates(im, [Xsamplinggrid.ravel(), Ysamplinggrid.ravel()], order=3, mode='nearest').reshape(Xsamplinggrid.shape) #This function does the same as interp2, it interpolates the 2D gridded data in meshgrid format
               ##     plt.figure(), plt.imshow(allprofiles) #$$$$$$$$$$$$$$$$$$$$$#
                    (rara,aa)=np.shape(Xsamplinggrid)#This measures the size of the array, the aa and rara are flipped because it is the other way around in python
                    spokesnoperquad=int(np.round(aa/4))#This function rounds the numbers in the array
                
                    Qiprofs=np.zeros((4,rara))#This creates an empty array which can be filled just like the functions above
                    Qiprofs[0,]=np.nanmean(allprofiles[:,0:spokesnoperquad], axis =1) #This is the east part, it is flipped because that was chosen above to do say compared to the matlab code
                    Qiprofs[1,]=np.nanmean(allprofiles[:,spokesnoperquad+1:2*spokesnoperquad], axis=1) #This is the north part
                    Qiprofs[2,]=np.nanmean(allprofiles[:,2*spokesnoperquad+1:3*spokesnoperquad], axis =1) #This is the west part
                    Qiprofs[3,]=np.nanmean(allprofiles[:,3*spokesnoperquad+1:4*spokesnoperquad], axis=1) #This is the south part
                
                    QiHor=np.concatenate((np.flip(Qiprofs[2,]),Qiprofs[0,]))#This functions makes an array of the  Horizontal and vertical part. Herefore the QIprofs[3,] is flipped right to left
                    QiVer=np.concatenate((np.flip(Qiprofs[3,]),Qiprofs[1,]))#This functions makes the Vertical part
                
                    fudgefactor=(np.pi/2)#This is explained in Loenhout, 2012
                #The following functions get the centered position of the image, which correction for oversampling and off center sampling
                    xnw=-((np.size(QiHor)/2-self.SymCenter(QiHor))+0.5)/QI['radialoversampling']/fudgefactor+xnw
                    ynw=-((np.size(QiVer)/2-self.SymCenter(QiVer))+0.5)/QI['radialoversampling']/fudgefactor+ynw
                    errx[ii]=((xnw-xol)**2+(ynw-yol)**2) #This calculates the error in the new and old location of x and y
                    if (np.isnan(xnw) or np.isnan(ynw)): #This function checks if one of the arrays returns Nan if that is the case the loop stops
                        prequit=1
                
                else:
                    prequit=1
                    xnw=xol
                    ynw=yol #After checking all the iterations the new locations are set
        
           ## print(xm,ym,xnw,ynw) #Here the values are printed
            if (np.isnan(xnw) or np.isnan(ynw)): #This checks if there are NaN values present. If this is the case it is repeated
                xnw=xol
                ynw=yol
         
            return xnw,ynw, allprofiles
    
    def SymCenter(self,prf): #This function is used to find the symmetry center of an array
        mp=np.nanmean(prf) #This function returns the mean of the array after removing all of the NaN values
        sel=np.where(np.isnan(prf)) #This function pads the NaNs because it first determines the NaNs and finds them afterwards
        prf[sel]=mp
        fw=prf-np.nanmean(prf) #Going forward 
        rv=np.flipud(prf)-np.nanmean(prf) #Reversing 
        d=np.real(np.fft.ifft(np.fft.fft(fw)*np.conj(np.fft.fft(rv)))) #Here the real part of the multiplication of the complex conjugated fouriertransform and inverse fourier transform are taken
        ld=np.ceil(np.size(d)/2) #This function rounds the number of the size of the array upwards
        d= np.concatenate((d[int(ld)+1:int(np.size(d))],d[1:int(ld)]))#Here the first and second half are swapped
        val=d.max(axis=0) #Takes the maximum of the array elements
        x = d.argmax(axis=0) #Returns the indices of the maximum value in the array in that certain axis
        x=(self.subpix_step(d)+np.size(prf)/2)/2 #Here the value for x is determined with the next function
        return x
        
    def subpix_step(self,d): #This function as described above calculates the sub pixel step
        #This is achieved with again a parabolic fitting
        hf=3
        ld=len(d)#the length of d is taken 
        xs=np.arange(0,ld)#Here an array is made from 0 to the value of ld
        x=np.argmax(d)#returns the indices of the maximum value of the array 
        lo= np.hstack([x-hf,1]).max()#These lines are for cropping. This function stacks the arrays collumn wise and takes the maximum value. 
        hi = np.hstack([x+hf,ld]).min()#This line takes the minimum
        ys=d[lo:hi]
        xs=xs[lo:hi]
        prms=np.polyfit(xs,ys,2)#Here the location is polyfitted
        x=-prms[1]/(2*prms[0])
        return x