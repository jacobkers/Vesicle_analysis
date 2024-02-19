import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from readlif.reader import LifFile

import guv_tools
from pathlib import Path

# from my custom devlop tools:
import sys


sys.path.append(
    "D:/jkerssemakers/Dropbox/CD_recent/BN_CD23_Jacob/analysis_general/code_development/python/",
)
from qi_trak import QI_Tracker

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


def work_radial_pattern(im, x0,y0,r0):
    dum=1
    return dum
    

for im_ori_name in movienames:
    source = im_ori_path + im_ori_name + str(suffix)
    csv_source = im_ori_path + str("Overlay Elements of ") + im_ori_name + str(".csv")
    guv_xyr = []
    XX0, YY0, RR0 = guv_tools.get_roi_info(csv_source)
    for ii, X0 in enumerate(XX0):
        thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
        guv_xyr.append(thisguv)
    N_guvs, dum = np.shape(guv_xyr)
    fig, axs = plt.subplots(N_guvs + 1, 5)
    with nd2reader.Nd2(source) as images:
        for ci, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
            for (
                color_i,
                chan,
            ) in enumerate(images):  #work each channel                
                #map_and_show:
                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*1.5
                roi = guv_tools.get_roi(chan, x0, y0, r0)
                if color_i==0: #setup work image for edge detection etc
                  work_image=guv_tools.sobel_it(roi)
                else:
                  work_image=work_image+guv_tools.sobel_it(roi)
                roi_array = np.array(roi)  #for tracking
                #build a work image-------------------------------------------     
                if color_i==0: #setup QI_track
                    QI=QI_Tracker(roi_array)
                    preset=QI_Tracker.TrackXY_by_QI_Init(QI,roi_array)                                                 
                # sample rim
                # clean               
                xq, yq = QI_Tracker.TrackXY_by_QI(QI,roi_array, preset, r0, r0)   
                # plotting cosmetics:-------------------------------------------
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
        outfig = datapath_out  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig)
print("Press any key to end demo")
input()


