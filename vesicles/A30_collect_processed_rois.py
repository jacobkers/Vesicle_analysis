"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

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
                writer = csv.writer(csv_f, delimiter=";")
                writer.writerow(data_row.values())

    if initval.suffix =='.tif'and initval.sequence=='time_trace':
        fig, axs = plt.subplots(2, 3, figsize=(20, 15))
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
                plot_ax = []
                R_minor = []
                R_major= []
                all_areas = []
                area = []
                perimeter = []
                roundness = []
                color0_inside = []
                c0_edge_mx = []
                c0_edge_sum = []
                c0_edge_sum_std = []
                c0_outside = []
                c0_contour_L = []
                c0_contour_ratio = []

                for fri, row in enumerate(data):
                    # ... (data processing code)
                    c0_mean_peaks = (float(row['c0_edge_mx']))
                    c0_sum = float(row['c0_edge_sum'])
                    okay_point = 1
                    if okay_point:
                        # fetch work parameters:
                        R_major.append(float(row['R_major']))
                        R_minor.append(float(row['R_minor']))
                        area.append(float(row['area']))
                        all_areas.append(float(row['all_areas']))
                        perimeter.append(float(row['perimeter']))
                        roundness.append((float(row['roundness'])))
                        color0_inside.append((float(row['color0_inside'])))
                        c0_edge_mx.append((float(row['c0_edge_mx'])))
                        c0_edge_sum.append((float(row['c0_edge_sum'])))
                        c0_edge_sum_std.append((float(row['c0_edge_sum_std'])))
                        c0_outside.append((float(row['c0_outside'])))
                        c0_contour_L.append((float(row['c0_contour_L'])))
                        c0_contour_ratio.append((float(row['c0_contour_ratio'])))

                        # build plots:
                        plot_ax.append(this_guv.dt * fri)
                        area.append(float(row['area']))
                        roundness.append(float(row['roundness']))
                        c0_edge_mx.append(c0_mean_peaks)
                        c0_edge_sum.append(float(row['c0_edge_sum']))

                simbol_color = movie_simbol_list[movie_use_index]
                sz = 2
                # Plot various metrics
                axs[0, 0].plot(area, 'o-', markersize=sz, color=simbol_color)
                axs[0, 0].set_ylabel("area")
                axs[0, 0].set_xlabel("time")
                axs[0, 0].set_title("area")

                axs[0, 1].plot(color0_inside, 'o-', markersize=sz, color=simbol_color)
                axs[0, 1].set_ylabel("I, a.u.")
                axs[0, 1].set_xlabel("time")
                axs[0, 1].set_title("color0_inside")

                axs[0, 2].plot(c0_outside, 'o-', markersize=sz, color=simbol_color)
                axs[0, 2].set_ylabel("I, a.u.")
                axs[0, 2].set_xlabel("time")
                axs[0, 2].set_title("color0_outside")

                plt.tight_layout()


if __name__ == "__main__":
    main()

