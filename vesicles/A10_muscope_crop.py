"""
21-2-2024
Work guv imagery, saves to standardized tiffs per guv
@author: jkerssemakers
"""
import numpy as np
import xarray as xr
from vesicles.common_tools import guv_io

""" 
experiment indices (add 0.1 to run on K:):
0: .nd testfiles
1: .lif testfiles 
"""
#expi = 0.2
#initval = get_exps(expi)

def set_up_xarray(XX0,YY0,RR0):
    """"
    here I create an x-array as a general 'GUV' data container
    I'll keep the cropped tiffs and masks outside for access by other programs (such as image J)
    I also save some illustrations for quick evalaution, per GUV. So for now, save only
    XYR as from the roi file is included
    """
    n_guvs=len(XX0)

    X0 = xr.DataArray(XX0, dims=("index",), coords={"index": np.arange(n_guvs) }, name="X0" )
    Y0 = xr.DataArray(YY0, dims = ("index",), coords = {"index": np.arange(n_guvs)}, name = "Y0" )
    R0 = xr.DataArray(RR0, dims=("index",), coords={"index": np.arange(n_guvs)}, name="R0")
    X_Guvs = xr.Dataset({"X0": X0, "Y0": Y0, "R0": R0})

    return X_Guvs

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

        #build a list of crop info:
        for ii, X0 in enumerate(XX0):
            thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
            guv_xyr.append(thisguv)

        # setup Xarray
        target=initval.mainpath_out + initval.subdir + "all_guvs.nc"
        XGuvs=set_up_xarray(XX0,YY0,RR0)
        XGuvs.to_netcdf(target)
        print(XGuvs)


        # acces microscope data and save to ROI-stacks per guv:
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