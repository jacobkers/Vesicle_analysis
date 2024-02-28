"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import guv_tools
import guv_io
from A00_init import get_exps

""" 
experiment indices (add 0.1 to run on K:):
0: .nd testfiles
1: .lif testfiles 
"""
expi = 1.1
initval = get_exps(expi)

for im_ori_name in initval.movienames:
    #source = initval.mainpath_in + initval.subdir + im_ori_name + str(initval.suffix)
    csv_source = initval.mainpath_in + initval.subdir + str("Overlay Elements of ") + im_ori_name + str(".csv")
    guv_xyr = []
    XX0, YY0, RR0 = guv_io.get_roi_info(csv_source)
    for ii, X0 in enumerate(XX0):
        thisguv = [int(X0), int(YY0[ii]), int(RR0[ii])]
        guv_xyr.append(thisguv)
        if initval.suffix == ".nd2":
            guv_io.cut_nd2_to_roi_tiffs(im_ori_name,guv_xyr,initval)
        if initval.suffix =='.lif': 
            guv_io.cut_lif_to_roi_tiffs(im_ori_name,guv_xyr,initval)
print("Press any key to end demo")
input()


