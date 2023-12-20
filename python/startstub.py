
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from pathlib import Path
from skimage import io
from copy import deepcopy
from scipy.ndimage import center_of_mass  # for calculation of image COM


fig, axs = plt.subplots(1, 4)

filnam="DOPC_DOPS_40 uM LUVs_1.nd2"
coord=[[99,136],[373,326]]

with nd2reader.Nd2(filnam) as images:
    for ii, chan, in enumerate(images):
        axs[ii].imshow(chan)
        for cd in coord:
            x=cd[0]
            y=cd[1]
            axs[ii].plot(x,y,'ro')
            axs[ii].set_title(images.channels[ii])
    fig.tight_layout()
    fig.show()
    print("Press any key to end demo")
    input()

    dum=1