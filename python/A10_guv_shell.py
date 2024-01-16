import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from readlif.reader import LifFile
import csv
from pathlib import Path
from scipy.ndimage import sobel
# from my custom devlop tools:
import sys
import cv2

sys.path.append(
    "D:/jkerssemakers/Dropbox/CD_recent/BN_CD23_Jacob/analysis_general/code_development/python/",
)
from how_to_do_it_examples.images import tracker_QI_practicum_MD as qit, image_cuts

# local:
from A00_init import get_exps

Experiments = get_exps()
expi = 0
mainpath_in = Experiments[expi].mainpath_in
mainpath_out = Experiments[expi].mainpath_out
movienames = Experiments[expi].movienames
subdir = Experiments[expi].subdir
suffix=Experiments[expi].suffix


im_ori_path = mainpath_in + subdir
datapath_out = mainpath_out + subdir
testpath = Path(datapath_out)
if not testpath.is_dir():
    testpath.mkdir()

def get_roi_info(csv_source):
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

def sobel_it(roi):
    roi = cv2.filter2D(roi, -1, 5)
    sobel_h = sobel(roi, 0)  # horizontal gradient
    sobel_v = sobel(roi, 1)  # vertical gradient
    magnitude = np.sqrt(sobel_h**2 + sobel_v**2)
    #magnitude *= 255.0 / np.max(magnitude)  # normalization
    return magnitude

for im_ori_name in movienames:
    source = im_ori_path + im_ori_name + str(suffix)
    csv_source = im_ori_path + str("Overlay Elements of ") + im_ori_name + str(".csv")

    guv_xyr = []
    XX0, YY0, RR0 = get_roi_info(csv_source)
    for ii, X0 in enumerate(XX0):
        thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
        guv_xyr.append(thisguv)

    N_guvs, dum = np.shape(guv_xyr)

    fig, axs = plt.subplots(N_guvs + 1, 5)


    with nd2reader.Nd2(source) as images:
        for ci, cd in enumerate(guv_xyr):  #work each GUV
            for (
                color_i,
                chan,
            ) in enumerate(images):  #work each channel 
                
                #map_and_show


                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*1.5
                roi = image_cuts.get_roi(chan, x0, y0, r0)
                if color_i==0: #setup work image
                  work_image=sobel_it(roi)
                #else:
                  #work_image=work_image+sobel_it(roi)    

                roi_array = np.array(roi)  #for tracking
                #build a work image-------------------------------------------     
                if color_i==0: #setup QI_track
                    QI=qit.QI_Tracker(roi_array)
                    preset=qit.QI_Tracker.TrackXY_by_QI_Init(QI,roi_array)
                                                  
                # sample rim
                # clean
                
                xq, yq = qit.QI_Tracker.TrackXY_by_QI(QI,roi_array, preset, r0, r0)   
                #-------------------------------------------
                axs[ci + 1, color_i].imshow(roi)
                plotgridx=preset["X0samplinggrid"]+xq
                plotgridy=preset["Y0samplinggrid"]+yq
                lx=np.shape(plotgridx)
                axs[ci + 1, color_i].plot(plotgridx[::10,::20],plotgridy[::10,::20],'r-',linewidth=0.3)
                axs[ci + 1, color_i].plot(xq,yq,'rx')
                axs[ci + 1, 4].imshow(work_image)
                axs[0, color_i].imshow(chan)
                axs[0, color_i].set_title(images.channels[color_i])
            axs[1, 4].set_title('work image')              
        fig.tight_layout()
        fig.show()
        outfig = datapath_out + im_ori_name + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig)
print("Press any key to end demo")
input()


