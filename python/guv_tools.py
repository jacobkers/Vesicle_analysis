#guv_tools
#tools to work with guv files:
import csv
import numpy as np
from scipy.ndimage import sobel


def get_roi(image,x0,y0,r0):
    """
    basic collection of points
    @author: jkerssemakers, 2024
    """
    #cuts square area with inscribed radius r0. If outside-roi, roi is shifted
    rr,cc =np.shape(image)
    lox=int(max([0, x0 - r0]))
    hix=int(min([cc, x0+r0]))
    loy=int(max([0, y0 - r0]))
    hiy=int(min([cc, y0+r0]))

    roi = image[loy:hiy, lox:hix]

    return roi

def get_roi_info(csv_source):
    """ ead roi data as acquired via ImageJ:
    ImageJ area selection
    * Open BF or Phase image
    * Select "round" ROI (keep Shift pressed for a circle)
    * Find the position and press "T" to load it into the ROI manager (check "show all" box)
    * Click into the ROI manager window and CTRL+A to select all ROIs
    * CLick More>list>File>Save As> ".....csv"
    * for convenience, you might just save the screenshots with overlays """
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