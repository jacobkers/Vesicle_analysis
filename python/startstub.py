
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
import csv
from pathlib import Path

#from my custom devlop  tools:
import sys
sys.path.insert(0, 'D:/jkerssemakers/Dropbox/CD_recent/BN_CD23_Jacob/analysis_general/code_development/python/')
from how_to_do_it_examples.images import QI_tracker_tools, image_cuts

#following should be more dir-based:
mainpath_in=str("M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/")
mainpath_out=str("M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/")
if 0:    
    im_ori_path = mainpath_in
    im_ori_name = str("DOPC_DOPS_40 uM LUVs_1")
if 1:
    subdir=str("60 uM_1h incubation/")    
    im_ori_names = [str("1"), str("2")]

im_ori_path = mainpath_in + subdir
datapath_out= mainpath_out + subdir
testpath=Path(datapath_out)
if not testpath.is_dir():
        testpath.mkdir()

for im_ori_name in im_ori_names:
    source = im_ori_path + im_ori_name +str(".nd2")
    csv_source= im_ori_path + str("Overlay Elements of ") + im_ori_name +str(".csv")

    def get_roi_info(csv_source):
        Xc=[]
        Yc=[]
        width=[]   
        with open(csv_source) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                Xc.append(float(row['X']))
                Yc.append(float(row['Y']))
                width.append(float(row['Width']))     

        XX0=(np.array(Xc)+np.array(width)/2)
        YY0=(np.array(Yc)+np.array(width)/2)
        RR0=(np.array(width)/2)
        
        return XX0, YY0,RR0


    guv_xyr=[]
    XX0, YY0,RR0 = get_roi_info(csv_source)
    for ii, X0 in enumerate(XX0):
        thisguv=[int(X0), int(YY0[ii]), int(RR0[ii])]
        guv_xyr.append(thisguv)

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
        outfig = datapath_out + im_ori_name + str("frame")+ str(1) + str(".png")
        #outfig = f"frame{frame_index}_plotname.png"
        fig.savefig(outfig)
print("Press any key to end demo")
input()

    #actions to do
        #crop box on center estimate
        #find center accurately
        #fin  rim (circle, ellipsoid) --> use radial mapper
        #sample rim
        #clean
