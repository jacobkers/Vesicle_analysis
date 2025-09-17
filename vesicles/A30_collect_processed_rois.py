"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import csv
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from scipy.interpolate import make_interp_spline
from vesicles.common_tools import guv_process_stacks
from vesicles.common_tools import guv_io
from vesicles.A00_init import get_exps

class GUV:
    """
    properties of a single guv movie
    """
    def __init__(self):
            #priority	identifier	comment	format	nZ	dT [s]	path in_order_of_appearance
            self.exp_id=0
            self.label='any_label'
            self.comment=[]
            self.use_it=[]
            self.crop_it=[]
            self.dt=1       

def main(initval,Guv_list, movie_to_use_list):
    movie_simbol_list = ['r', 'k', 'b']
    if initval.suffix =='.tif'and initval.sequence=='single_frame':
        #collect single-frame data points and re-save all in one file
        load_dirname=initval.mainpath_out + initval.subdir +str("/A20b_processed/")
        csv_path_in = Path(load_dirname)
        name=[]
        X=[]
        Y=[]
        data=[]
        for csv_source in csv_path_in.glob("**/*.csv"):  # find all relevant csv files in inpath
            print(csv_source.stem)
            with open(csv_source) as f:
                reader = csv.DictReader(f, delimiter=";")
                for row in reader:
                    name.append(csv_source.stem)
                    data.append(row)
        #set up csv for tracking data:
        csv_path_out = Path(initval.mainpath_out + initval.subdir +str("/A30_processed/"))
        if not csv_path_out.is_dir():
                csv_path_out.mkdir()

        csv_target=load_dirname  + "collected_data" + str(".csv")
        with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
            # create the csv writer
            writer = csv.writer(csv_f, delimiter=";")
            #f = open("test.csv", "a")
            writer.writerow(row.keys())
            for data_row in data:

                # create the csv writer
                writer = csv.writer(csv_f, delimiter=";")
                #f = open("test.csv", "a")
                writer.writerow(data_row.values())
            dum=1


    if initval.suffix =='.tif'and initval.sequence=='time_trace':
        fig, axs = plt.subplots(2, 4, figsize=(20, 15))
        load_dirname_A20a = initval.mainpath_out + initval.subdir + "/A20a_tracked/"
        load_dirname_A20b = initval.mainpath_out + initval.subdir + "/A20b_processed/"
        guv_labels = []
        for this_guv in Guv_list:
            if this_guv.use_it == 1 and this_guv.movie_id in movie_to_use_list:
                movie_use_index = movie_to_use_list.index(this_guv.movie_id)
                guv_labels.append(this_guv.label)

                # Read data from CSV
                csv_source = Path(load_dirname_A20b + this_guv.label + "_all_data.csv")
                with open(csv_source) as g:
                    reader = csv.DictReader(g, delimiter=";")
                    data = list(reader)
                # Process and plot data
                plot_ax, area, roundness, major_minor = [], [], [], []
                c0_edge_mx, c0_edge_sm = [], []

                for fri, row in enumerate(data):
                    # ... (data processing code)
                    c0_mean_peaks = (float(row['c0_edge_mx']))
                    c0_sum = float(row['c0_edge_sum'])
                    okay_point = 1
                    if okay_point:
                        # fetch work parameters:
                        axis_major = float(row['R_major'])
                        axis_minor = float(row['R_minor'])
                        c0_mean_peaks = (float(row['c0_edge_mx']))
                        # build plots:
                        if 1:
                            plot_ax.append(this_guv.dt * fri)
                            axlabel = "time (s)"
                        area.append(float(row['area']))
                        roundness.append(float(row['roundness']))
                        c0_edge_mx.append(c0_mean_peaks)
                        c0_edge_sm.append(float(row['c0_edge_sum']))

                simbol_color = movie_simbol_list[movie_use_index]
                sz = 2
                # Plot various metrics
                axs[0, 0].plot(plot_ax, area, 'o-', markersize=sz, color=simbol_color)
                axs[0, 0].set_ylabel("area")
                axs[0, 0].set_title("area")
                # ... (more plotting code for other metrics)
                plt.tight_layout()


if __name__ == "__main__":
    main()

