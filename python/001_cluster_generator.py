
import numpy as np
import cv2
import pickle 
import matplotlib.pyplot as plt

from pathlib import Path
from skimage import io
from copy import deepcopy
from scipy.ndimage import center_of_mass  # for calculation of image COM
from MD_tresholder_1d import get_treshold_data


class Gbox:
    """
    A Gbox, or genome-in-a-box, is a collection of properties associated with a
      single genome-in-a box image,
    such as the frame index, image center-of-mass, composing clusters, composing spotcomponents
    """

    def __init__(self):
        Gbox.frame_index = 1
        Gbox.COM = [0, 0]
        Gbox.Noise = 0
        Gbox.clusters = []


class Cluster:
    """
    A cluster is a group of gaussian spot-components, each within one psf_decompose distance of at east one other
    Together they form an optically smooth pattern of any shape and size
    """

    def __init__(self):
        self.spots = []

class Spot:
    """
    A spot,  is a single Gaussian spot with position and amplitude
    It is used as a minimal building block for describing clusters
    """
    def __init__(self):
        self.x = 0  # x-position
        self.y = 0  # y-position 
        self.pk = 0  # peak value, as-found
        self.pc = 0  # peak value, % of total of this image
        self.pr = 0  # peak value, relative to spot treshold of this image

def init_cluster(inspots):
    """
    A cluster is seeded by taking the next spot from a collection
    """
    thiscluster = Cluster()
    # add first element to new cluster:
    thiscluster.spots = [inspots[0]]
    # shrink remaining spots:
    outspots = inspots[1:]

    return thiscluster, outspots

def read_spotlist(spotlist):
    # flatten spotlist content for array-based actions
    xx = []
    yy = []
    pk = []
    pc = []
    pr = []
    for Spot in spotlist:
        xx.append(Spot.x)
        yy.append(Spot.y)
        pk.append(Spot.pk)
        pc.append(Spot.pc)
        pr.append(Spot.pr)
    xx = np.array(xx)
    yy = np.array(yy)
    pk = np.array(pk)
    pc = np.array(pc)
    pr = np.array(pr)
    return xx, yy, pk, pc, pr

def grow_cluster(thiscluster, spotstock, minR):
    """
    Recruitment: transfer nearby spots from the stock to this cluster
    Nearby means: only iF the spot is within one point spread function of at least one
    of the existing cluster-associated spots
    """
    newly_added_spots = []
    for ii, val in enumerate(thiscluster.spots):
        spotstock_xx, spotstock_yy = read_spotlist(spotstock)[0:2]
        spotstock_new = []
        spot_x0 = thiscluster.spots[ii].x
        spot_y0 = thiscluster.spots[ii].y
        rr = np.hypot(spotstock_xx - spot_x0, spotstock_yy - spot_y0)
        # near_i =np.nonzero(rr <= np.min(rr))
        nearby_ixes = np.nonzero(rr <= minR)[0]
        far_away_ixes = np.nonzero(rr > minR)[0]
        # recruit:
        if len(nearby_ixes) > 0:
            more_nearby = 1
            # add Spot to cluster list
            for n_ix in nearby_ixes:
                newly_added_spots.append(spotstock[n_ix])
            # strip Spot from spot stock
            for f_ix in far_away_ixes:
                spotstock_new.append(spotstock[f_ix])
            spotstock = spotstock_new
        else:
            more_nearby = 0
    # recruit new ones
    for newspot in newly_added_spots:
        thiscluster.spots.append(newspot)
    return thiscluster, spotstock, more_nearby


def group_cluster(spotstock, psf_decompose):
    """
    group the available spot-components in separate clusters until all chosen spots are accounted for
    """
    clusters = []
    while len(spotstock) > 0:
        # add first element to new cluster
        thiscluster, spotstock = init_cluster(spotstock)
        thiscluster.ID_no = len(clusters) + 1
        # find all other connected spots:
        more_nearby = 1
        while more_nearby:
            # recruit spots for this cluster from the stock:
            minR = 1.0 * psf_decompose
            thiscluster, spotstock, more_nearby = grow_cluster(
                thiscluster, spotstock, minR
            )
        clusters.append(thiscluster)
    return clusters


def spotpeeler(work_im):
    """
    spot decomposition:
    starts with a work image. Image max is diminished by a gaussian spot of same amplitude, spot is added to a 'build' image.
    This is done iteratievely until end-of-sequence, resulting in
    a list of spots in order of amplitude, the image they compose and the residu
    """
    #
    residu_im = deepcopy(work_im)
    # residu_im = work_im - np.median(work_im)
    residu_im[np.nonzero(residu_im < 0)] = 0  # shave off

    Fc = np.sum(residu_im)
    build_im = 0 * residu_im

    # first, decompose image in spots:
    # we start the loop
    spotlist = []
    keep_going = 1
    while keep_going:
        # remove inadvertent over-peeling:
        residu_im[np.nonzero(residu_im < 0)] = 0
        # get new maximum spot:
        nextspot = Spot()
        pk = np.amax(residu_im)
        pickspot = np.argwhere(residu_im == pk)
        nextspot.y = pickspot[0, 0]
        nextspot.x = pickspot[0, 1]

        # build a gauss spot around image maximum:
        RR = np.hypot(XX - nextspot.x - 1, YY - nextspot.y - 1)
        spot_im = pk * np.exp(-(RR**2 / ((psf_decompose / 2) ** 2)))

        # peel off and add to 'build' image:
        residu_im = residu_im - spot_im
        build_im = build_im + spot_im
        # collect counts and percentage of total intensity covered:
        spot_perc = np.sum(spot_im) / Fc * 100
        build_perc = np.sum(build_im) / Fc * 100
        nextspot.pk = pk
        nextspot.pc = spot_perc   
        # add the new spot to the lists
        spotlist.append(nextspot)
        keep_going = build_perc < 100
    return spotlist, build_im, residu_im


def split_brightlights(spotlist):
    # analyze spot list
    # 1 get cutoff:
    pc = read_spotlist(spotlist)[3]
    treshold_perc = get_treshold_data(pc)
    # 2 sub_categorize in 'fat' and 'flutter' spots:
    spotlist_fat = []
    spotlist_flutter = []
    for spot in spotlist:
        if spot.pc > treshold_perc:
            spotlist_fat.append(spot)
        else:
            spotlist_flutter.append(spot)
    return spotlist_fat, spotlist_flutter, treshold_perc

psf_presmooth = 5
psf_decompose = 3

#  load image:
# im_ori_path = Path(r"M:\tnw\bn\alg\Shared\Jacob\Traps\test_images")
# laptop:
if 0:
    im_ori_path = Path(r"C:\Users\jkerssemakers\CD_Data_in\2023_Alex\test_images")
    im_ori_name = str("AlexJ_nuc_22sept_4820230203_35327 PMc1_area1-1.tif")
# shared
if 0:
    im_ori_path = Path(r"M:\tnw\bn\alg\Shared\Jacob\Traps\test_images")
    im_ori_name = str("Substack (786-1000)-1_area1-1.tif")
    im_ori_name = str("AlexJ_nuc_22sept_4820230203_35327 PMc1_area0-1.tif")
# stack per frame
if 0:
    im_ori_path = Path(r"M:\tnw\bn\cd\Shared\Jacob\TESTdata_in\Alex\single_images")
    im_ori_name = str("AlexJ_nuc_22sept_4820230203_35327 PMc1_area10800.tif")
# stack
if 1:
    im_ori_path = Path(r"M:\tnw\bn\cd\Shared\Jacob\TESTdata_in\Alex\Traps\testdata_cut")
    im_ori_name = str("AlexJ_nuc_22sept_4820230203_35327 PMc1_area1.tif")

plots_out_path = Path(
    r"D:\jkerssemakers\Dropbox\CD_Data_out\2023_Alex\2023_10_02 cluster_test\frames_1"
)

# load image, pre_clean, set up stuff
ori_im_st = io.imread(im_ori_path / f"{im_ori_name}")
work_im0 = ori_im_st[0, :, :]
work_im1 = cv2.GaussianBlur(ori_im_st[0, :, :], (3, 3), 0)

#crop it
ori_im_st=ori_im_st[1:100, :, :]

ff, rr, cc = np.shape(ori_im_st)
global_treshold = get_treshold_data(np.reshape(work_im1, rr * cc))

frame_index = 0
LifeInABox = []
N_clusters = []
Content_clusters = []
Fluorescence_all = []
nbins=50
minbin=0
maxbin=5
binax = np.linspace(minbin, maxbin, nbins)
midax=binax[0:-1]+np.diff(binax)
pixels_histmap = np.zeros((ff, nbins-1))
spot_histmap = np.zeros((ff, nbins-1))

for ori_im in ori_im_st:
    frame_index = frame_index + 1
    # coordinate pictures and setup:
    rr, cc = np.shape(ori_im)
    vx, vy = np.linspace(1, rr, rr), np.linspace(0, cc, cc)
    XX, YY = np.meshgrid(vy, vx)

    # smooth and background correct:
    work_im = (
        cv2.GaussianBlur(ori_im, (psf_presmooth, psf_presmooth), 0) - global_treshold
    )
    work_im[np.nonzero(work_im<  0)] = 0  #shave off
    # get spots:
    spotlist, build_im, residu_im = spotpeeler(work_im)
    # split:
    spotlist_fat, spotlist_flutter, treshold = split_brightlights(spotlist)
    # group the larger spots in clusters
    clusters = group_cluster(spotlist_fat, psf_decompose)

    # get relative content for this image:
    content_all = np.sum(read_spotlist(spotlist)[2])
    content_fat = np.sum(read_spotlist(spotlist_fat)[2])

    # add data to timeline:
    Content_clusters.append(100 * content_fat / content_all)

    Fluorescence_all.append(np.sum(build_im))

    # histograms per frame
    pixels = np.reshape(work_im - global_treshold, rr * cc)
    pixels_hist_thisframe, edges = np.histogram(pixels, binax)
    pixels_histmap[frame_index - 1, :] = pixels_hist_thisframe
    spot_hist_thisframe, edges = np.histogram(read_spotlist(spotlist)[3], binax)
    spot_histmap[frame_index - 1, :] = spot_hist_thisframe

    # add extra info for this frame
    ThisGbox = Gbox()
    ThisGbox.frame_index = frame_index
    ThisGbox.COM = center_of_mass(build_im)
    ThisGbox.clusters = clusters
    ThisGbox.N_clusters = len(clusters)
    ThisGbox.clustercontent_all = content_all
    ThisGbox.clustercontent_fat = content_fat
    ThisGbox.clustercontent_fluffy = content_all - content_fat
    N_clusters.append(len(clusters))

    # add gbox state to the lifeline for later use:
    LifeInABox.append(ThisGbox)

    # show:
    print(frame_index)
    badcodinghabit = 1
    if (badcodinghabit & ((np.mod(frame_index, 5) == 0))) | frame_index == ff - 1:
        fig, axs = plt.subplots(2, 2)
        axs[0, 0].imshow(work_im)
        axs[0, 0].set_title("decomposed")
        for fatspot in spotlist_fat:
            axs[0, 0].plot(fatspot.x, fatspot.y, "wo", markersize=2)
        for flutterspot in spotlist_flutter:
            axs[0, 0].plot(flutterspot.x, flutterspot.y, "bo", markersize=1)
        for cluster in clusters:
            spotx = []
            spoty = []
            for spot in cluster.spots:
                spotx.append(spot.x)
                spoty.append(spot.y)
            axs[0, 0].plot(spotx, spoty, "-o", markersize=3)
        axs[0, 0].set_title("per cluster")
        axs[0, 1].imshow(np.transpose(spot_histmap),extent=[minbin,maxbin,0,frame_index])
        axs[0, 1].set_aspect("auto")
        axs[0, 1].set_title("intensity histogram vs time")
        axs[0, 1].set_xlabel("frame")
        axs[0, 1].set_ylabel("intensity, a.u")
        axs[0, 1].set_xlim(0, 1000)
        axs[1, 0].plot(N_clusters, "ro", markersize=2)
        axs[1, 0].set_title("cluster count")
        axs[1, 0].set_xlim(0, 1000)
        axs[1, 0].set_ylim(0, 25)
        axs[1, 0].set_xlabel("frame")
        axs[1, 0].set_ylabel("counts, a.u")
        axs[1, 1].plot(Fluorescence_all, "bo", markersize=2)
        axs[1, 1].set_title("total fluorescence")
        axs[1, 1].set_xlim(0, 1000)
        axs[1, 1].set_xlabel("frame")
        axs[1, 1].set_ylabel("counts, a.u")
        fig.tight_layout()
        fig.show()

        # collect cluster spots
        if 0:
            pp_clust = []
            for cluster in clusters:
                for cspot in cluster.spots:
                    pp_clust.append(cspot.p)
            pp_clust.sort(reverse=True)
            # collect all spots:
            pp_all = []
            for spot in spotlist:
                pp_all.append(spot.p)
            pp_clust.sort(reverse=True)
            fig, axs = plt.subplots(1)
            axs.plot(pp_all, "k-")
            axs.plot(pp_clust, "ro")
            axs.set_title("cluster count")
            fig.tight_layout()
            fig.show()
            fig.set_size_inches(4.5 * cm, 4.5 * cm)
        fig.tight_layout()
        outfig = plots_out_path / f"frame{frame_index}_clusters.png"
        plt.savefig(outfig)
        print("Press any key to end demo")
        input()
        plt.close("all")
        # badcodinghabit = 0

#build a flat csv file from LifeInABox, per spot:
"""
frame index
cluster index
spot index
spot_x
spot_y
spot_pk : as found
spot_pc : percentage to image count
spot_bri_1 :relative to image treshold
spot_bri_2 :relative to stack treshold
 """

fig, axs = plt.subplots(1, 2)
axs[0].plot(N_clusters, "ro")
axs[0].set_title("cluster count")
axs[0].set_xlabel("frame")
axs[0].set_ylabel("count")
axs[1].plot(Content_clusters, "bo")
axs[1].set_title("cluster content percentage")
axs[1].set_xlabel("frame")
axs[1].set_ylabel("counts, a.u.")
fig.tight_layout()
fig.show()

#save results


print("Press any key to end demo")
input()
