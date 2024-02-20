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


# local:
from A00_init import get_exps
#build paths:
expi = 0
initval = get_exps(expi)

im_ori_path = initval.mainpath_in + initval.subdir
datapath_out = initval.mainpath_out + initval.subdir
testpath = Path(datapath_out)
if not testpath.is_dir():
    testpath.mkdir()


def work_radial_pattern(im, x0,y0,r0):
    dum=1
    return dum   


for im_ori_name in initval.movienames:
    source = im_ori_path + im_ori_name + str(initval.suffix)
    csv_source = im_ori_path + str("Overlay Elements of ") + im_ori_name + str(".csv")
    guv_xyr = []
    XX0, YY0, RR0 = guv_tools.get_roi_info(csv_source)
    for ii, X0 in enumerate(XX0):
        thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
        guv_xyr.append(thisguv)
    N_guvs, dum = np.shape(guv_xyr)
    fig, axs = plt.subplots(N_guvs + 1, 4)
    #loop: 'images' contains all colors and all frames
    with nd2reader.Nd2(source) as images:
        for ci, cd in enumerate(guv_xyr):  #work each GUV and its center coordinates:
            for (
                color_i,
                chan,
            ) in enumerate(images):  #work each color channel  per guv              
                #map, show, save:
                x0 = cd[0]
                y0 = cd[1]
                r0 = cd[2]*1.5               
                roi = guv_tools.get_roi(chan, x0, y0, r0)
                              
                #build a work image via the various channels-------------------------------------------   
                if color_i==0: #setup a work image for edge detection etc
                  #work_image=guv_tools.sobel_it(roi)
                  work_image=roi
                #else:
                  #work_image=work_image+guv_tools.sobel_it(roi)                
                
                # plotting cosmetics:-------------------------------------------
                axs[ci + 1, color_i].imshow(roi)               
                axs[0, color_i].imshow(chan)
                axs[0, color_i].set_title(images.channels[color_i])
                        
        fig.tight_layout()
        fig.show()
        outfig_name1 = datapath_out  + str("file_")+ im_ori_name  + str("frame") + str(1) + str(".png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig_name1)
                   
        #process the work image
        fig2, ax2 = guv_tools.work_radial_pattern(work_image, x0,y0,r0)
        fig2.show() 
        outfig_name2 = datapath_out  + str("file_")+ im_ori_name  + str("frame") + str(1) + str("_QI_track.png")
        # outfig = f"frame{frame_index}_plotname.png"
        fig2.savefig(outfig_name2)

print("Press any key to end demo")
input()


