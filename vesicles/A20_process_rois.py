"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
from vesicles.common_tools import guv_process_stacks
from vesicles.common_tools import guv_io
from vesicles.A00_init import get_exps

def main(initval,a=0,b=0):
    for im_ori_name in initval.movienames:
        #access ROI-stacks per guv:
        if a: guv_process_stacks.a20a_build_coordinates(im_ori_name,initval)
        if b: guv_process_stacks.a20b_map_color_channels(im_ori_name,initval)

if __name__ == "__main__":
    main()
