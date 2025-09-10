"""
21-2-2024
Work guv imagery, saves to standardized tiffs per guv
@author: jkerssemakers
""" 
from vesicles.common_tools import guv_io

""" 
experiment indices (add 0.1 to run on K:):
0: .nd testfiles
1: .lif testfiles 
"""
#expi = 0.2
#initval = get_exps(expi)

def main(initval):
    for im_ori_name in initval.movienames:
        #source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
        csv_source = initval.mainpath_in + initval.subdir + str("Overlay Elements of ") + im_ori_name + str(".csv")
        #build list of GUVs:
        guv_xyr = []
        XX0, YY0, RR0 = guv_io.get_roi_info(csv_source)

        if initval.apply_drift_correction==1:
            csv_drift = initval.mainpath_in + initval.subdir + im_ori_name + str("_drift.csv")
            initval.driftX, initval.driftY= guv_io.get_drift_info(csv_drift,initval)

        for ii, X0 in enumerate(XX0):
            thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
            guv_xyr.append(thisguv)
        #acces microscope data and save to ROI-stacks per guv:
        if initval.suffix == ".nd2":
            guv_io.cut_nd2_to_roi_tiffs(im_ori_name,guv_xyr,initval)
        if initval.suffix =='.lif': 
            guv_io.cut_lif_to_roi_tiffs(im_ori_name,guv_xyr,initval)
        if initval.suffix =='.tif' and initval.sequence=='time_trace':
            guv_io.cut_tif_to_roi_tiffs_hardwired(im_ori_name,guv_xyr,initval)
        if initval.suffix =='.tif' and initval.sequence=='single_frame':
            guv_io.cut_singletime_tif_to_roi_tiffs(im_ori_name,guv_xyr,initval)  # change this to a single frame operator

if __name__ == "__main__":
    main()