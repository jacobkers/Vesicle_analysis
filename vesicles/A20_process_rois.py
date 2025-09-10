"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
from vesicles.common_tools import guv_process_stacks
from vesicles.common_tools import guv_io
from vesicles.A00_init import get_exps


def main(initval):
    for im_ori_name in initval.movienames:
        #simage J coordinates:
        csv_source = initval.mainpath_in + initval.subdir + str("Overlay Elements of ") + im_ori_name + str(".csv")
        #build list of GUVs (just used for counting them, tiffs already exist):
        guv_xyr = []
        XX0, YY0, RR0 = guv_io.get_roi_info(csv_source)
        for ii, X0 in enumerate(XX0):
            thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
            guv_xyr.append(thisguv)
        #access ROI-stacks per guv:
        if 1: guv_process_stacks.a20a_build_coordinates(im_ori_name,guv_xyr,initval)
        if 1: guv_process_stacks.a20b_map_color_channels(im_ori_name,guv_xyr,initval)

if __name__ == "__main__":
    main()
