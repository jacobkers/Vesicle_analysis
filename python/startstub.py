
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from pathlib import Path

#from my custom devlop  tools:
import sys
sys.path.insert(0, 'D:/jkerssemakers/Dropbox/CD_recent/BN_CD23_Jacob/analysis_general/code_development/python/')
from how_to_do_it_examples.images import QI_tracker_tools, image_cuts

if 1:
    #following should go to json or so:
    im_ori_path = str("M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/")
    im_ori_path = str()
    im_ori_name = str("DOPC_DOPS_40 uM LUVs_1.nd2")

source = im_ori_path + im_ori_name 

plots_out_path = Path(
    r"D:\jkerssemakers\Dropbox\CD_Data_out\2023_Alex\2023_10_02 cluster_test\frames_1"
)


#[x y r]:
guv_xyr=[[99,136,150 ],[373,326, 150]]
N_guvs, dum=np.shape(guv_xyr)

fig, axs = plt.subplots(N_guvs+1, 4)

with nd2reader.Nd2(source) as images:   
    for ci, cd in enumerate(guv_xyr):
        for ii, chan, in enumerate(images): 
        #plot menu:
            axs[0, ii].imshow(chan)
            x0=cd[0]
            y0=cd[1]
            r0=cd[2]
            roi=image_cuts.get_roi(chan,x0,y0,r0)
            roi_array=np.array(roi)
            var = QI_tracker_tools.QI_Tracker(roi_array)
            axs[ci+1, ii].imshow(roi)
            axs[0,ii].plot(x0,y0,'ro')
            axs[0,ii].set_title(images.channels[ii])
    fig.tight_layout()
    fig.show()
    print("Press any key to end demo")
    input()

#actions to do
    #crop box on center estimate
    #find center accurately
    #fin  rim (circle, ellipsoid) --> use radial mapper
    #sample rim
    #clean

    dum=1