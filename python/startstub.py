
import numpy as np
import matplotlib.pyplot as plt
import nd2reader
from pathlib import Path
from skimage import io
from copy import deepcopy
from scipy.ndimage import center_of_mass  # for calculation of image COM


fig, axs = plt.subplots(1, 3)

with nd2reader.Nd2("DOPC_DOPS_40 uM LUVs_1.nd2") as images:
    axs[0].imshow(images[0])
    axs[1].imshow(images[1])
    axs[2].imshow(images[2])

    fig.tight_layout()
    fig.show()
    print("Press any key to end demo")
    input()

    dum=1