import numpy as np
import csv
import math as mt
from skimage import io
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tf
from common_tools import guv_tools
from common_tools.guv_io import load_tiff_movie, load_tiff_frame, load_nd2_movie, load_nd2_movie_try2

from Rafa.B00_init import get_exps

def extract_ring_values(intensity_array, center, Rmin, Rmax):
    # Get the dimensions of the 2D array
    rows, cols = intensity_array.shape   
    # Calculate the center coordinates
    if 0:
        center_x, center_y = rows // 2, cols // 2
    else:
        center_x=center[0]
        center_y = center[1]

    # Initialize an empty list to store values within the ring
    ring_values = []
    
    # Loop over each element in the 2D array
    for x in range(rows):
        for y in range(cols):
            # Calculate the Euclidean distance from the center
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # Check if the distance is within the ring boundaries
            if Rmin < distance <= Rmax:
                ring_values.append(intensity_array[x, y])            
    return np.array(ring_values)


def kymo(exps):
    for initval in exps:
        label=initval.unique_label
        moviepath=initval.moviepath
        savepath=initval.savepath
        movie_filename = initval.moviename
        filename =initval.spot_image    
        
        image_path =  moviepath + '/' + filename
        movie_path =  moviepath + '/' + movie_filename

        #load movie:
        if initval.suffix=='.tif':
            frames=load_tiff_movie(movie_path)
        if initval.suffix=='.nd2':
            frames=load_nd2_movie_try2(movie_path,initval.dyechannel)
            #frames=load_nd2_movie(movie_path,initval.dyechannel)
        
        
        frames_array=[]
        for fri, frame in enumerate(frames):
            print("B10:frame" + str(fri))
            frames_array.append(np.array(frame))
        frames_array=np.array(frames_array)

        #load events (start time and position of event)
        event_data_name=label +"_events" +  str(".csv")
        csv_events=savepath /  event_data_name
        csv_path_in = Path(csv_events)
        event_data = np.loadtxt(csv_events, delimiter=';')

        #define a zoomed, and a full kymograph:
        rws=initval.rws
        DT_list=initval.DT_list
        pre_shift_list=initval.pre_shift_list
        
        DX=70 
        DY=70
        #define a series of rings of constant surface, based on R0
        R0=10
        rings=[0, R0]
        if 1: #equal surface
            for i in np.arange(4):
                Ri=rings[i+1]
                R_nxt=(Ri**2+R0**2)**0.5
                rings.append(R_nxt)
        else:
            rings=[0,5, 10, 15, 20, 25, 30, 35]

        for event_no, event in enumerate(event_data): 
            print("B10:event" + str(event_no))
            fig, ax=plt.subplots(4,1)   
            #run twice: one time as full movie, one time as zoom
            for rw, DT, pre_shift in zip(rws, DT_list, pre_shift_list):   
                x0=int(event[1])
                y0=int(event[2])
                t0=np.max([0, int(event[0])+int(DT/2)-pre_shift])
                subarray, t_min, t_max, x_min, x_max, y_min, y_max=guv_tools.extract_subarray(frames_array, t0, x0, y0, DT, DX, DY)
                ringdata_intensity=[]
                ringdata_mn=[]
                ringdata_std=[]
                for fri, sub_frame in enumerate(subarray):
                    #print(fri)
                    #collect ring intensities:
                    intensity_rings=[]
                    intensity_rings_mn=[]
                    intensity_rings_std=[]
                    for ri in np.arange(len(rings)-1):  
                        #center= np.unravel_index(np.argmax(sub_frame), sub_frame.shape)
                        #center=[sub_frame.shape[1]/2, sub_frame.shape[0]/2]
                        center=[x0-x_min, y0-y_min]
                        ringvals=extract_ring_values(sub_frame, center, rings[ri], rings[ri+1])
                        intensity_rings.append(np.round(np.sum(ringvals)))
                        intensity_rings_mn.append(np.round(np.mean(ringvals)))
                        intensity_rings_std.append(np.round(np.std(ringvals)))
                    ringdata_intensity.append(intensity_rings)
                    ringdata_mn.append(intensity_rings_mn)
                    ringdata_std.append(intensity_rings_std)        
                
                #kymograph section:
                #sum:
                sumprojection_0=np.sum(subarray,axis=0)
                sumprojection_1=np.sum(subarray,axis=1) #keeps y around Y0
                sumprojection_2=np.sum(subarray,axis=2) #keeps x around X0
                if 0:
                    fig, ax=plt.subplots(1,1)  
                    ax.imshow(sumprojection_0, extent=[x_min,x_max,y_min, y_max])
                    ax.set_title('SUM_event' + str(event_no).zfill(4))
                    fig.show()
                    dum=1
                #choose full side if close to edge
                rr,cc= np.shape(sumprojection_0)
                if rr>cc:
                    used_proj=sumprojection_2
                    used_trace=np.sum(sumprojection_2.T,axis=0)
                    pos_min=y_min
                    pos_max=y_max
                else:
                    used_proj=sumprojection_1
                    used_trace=np.sum(sumprojection_1.T, axis=0)
                    pos_min=x_min
                    pos_max=x_max
                #show:
                if rw == 0:  #zoom
                    
                    ax[2].imshow(used_proj.T, aspect='auto', extent=[t_min,t_max,pos_min,pos_max])
                    ax[2].set_ylabel("pos, pixels")
                    ax[2].set_xlabel("Time,frames")              
                    ax[3].plot(ringdata_intensity, 'o', markersize=2)
                    ax[3].set_ylabel("sum intensity, a.u.")
                    ax[3].autoscale(enable=True, axis='x', tight=True)
                    ax[3].get_xaxis().set_visible(False)
                    t_start=t_min
                    t_stop=t_max
                if rw == 1: #overview
                    ax[0].plot(ringdata_intensity, 'o', markersize=2)
                    ax[0].legend(["center","ring"])
                    ax[0].set_ylabel("sum intensity, a.u.")
                    ax[0].autoscale(enable=True, axis='x', tight=True)
                    ax[0].get_xaxis().set_visible(False)
                    #white lines               
                    ax[1].imshow(np.log10(used_proj.T),aspect='auto', extent=[t_min,t_max,pos_min,pos_max,])
                    ax[1].plot([t_start,t_start],[pos_min,pos_max], 'w--',linewidth=0.5)
                    ax[1].plot([t_stop,t_stop],[pos_min,pos_max], 'w--',linewidth=0.5)
                    ax[1].set_ylabel("pos, pixels")

                fig.tight_layout()

                #final savings 
                kymopath =savepath / str('kymographs_' + label +'/')
                kymosubpath =savepath / str('kymographs_' + label +'/kymos/')
                csvpath = savepath / str('kymographs_' + label +'/csv/')
                if not kymopath.is_dir():
                    kymopath.mkdir()
                if not csvpath.is_dir():
                    csvpath.mkdir()
                if not kymosubpath.is_dir():
                    kymosubpath.mkdir()
                #overview png:
                if rw==1:
                    #jpeg overview:
                    kymo_overview_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_kymo.png")
                    kymo_path= savepath/  kymo_overview_name
                    fig.savefig(kymo_path)
                
                    #full traces center and ring
                    #save ring data as columns per event for simple handling  
                    savelabels=[str("_intensity"), str("_mean"),str("_std")]
                    savedata=[ringdata_intensity, ringdata_mn, ringdata_std]
                    for _savelabel, _ringdata in zip(savelabels,savedata):
                        trace_data_name='kymographs_' + label +'/csv/' + 'event' + str(event_no).zfill(4) +  str("_ring_traces") + _savelabel + str(".csv")
                        csv_target=savepath /  trace_data_name
                        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
                            # create the csv writer
                            writer = csv.writer(csv_f, delimiter=";")
                            for data_row in _ringdata:         
                                writer = csv.writer(csv_f, delimiter=";")
                                writer.writerow(data_row)

                #tiffs:
                if rw==0:
                    #tiff files zoom section:
                    ROI_movie_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_MV_zoom.tif")
                    io.imsave(savepath / f"{ROI_movie_name}", subarray, check_contrast=False)
                    
                    kymo0_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_XY_zoom.tif")
                    io.imsave(savepath / f"{kymo0_name}", sumprojection_0, check_contrast=False)

                    kymo1_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_XT_zoom.tif")
                    io.imsave(savepath / f"{kymo1_name}", sumprojection_1, check_contrast=False)

                    kymo2_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_YT_zoom.tif")
                    io.imsave(savepath / f"{kymo2_name}", sumprojection_2, check_contrast=False)
                if rw==1:
                    #tiff files full section:
                    ROI_movie_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_MV_full.tif")
                    io.imsave(savepath / f"{ROI_movie_name}", subarray, check_contrast=False)

                    kymo0_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_XY_full.tif")
                    io.imsave(savepath / f"{kymo0_name}", sumprojection_0, check_contrast=False)

                    kymo1_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_XT_full.tif")
                    io.imsave(savepath / f"{kymo1_name}", sumprojection_1, check_contrast=False)

                    kymo2_name = 'kymographs_' + label +'/kymos/' + 'event' + str(event_no).zfill(4) +  str("_YT_full.tif")
                    io.imsave(savepath / f"{kymo2_name}", sumprojection_2, check_contrast=False)
                
            plt.close('All')    



            







