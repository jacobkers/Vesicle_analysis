"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import xarray as xr
from vesicles.common_tools import guv_io

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

def main(initval):
    # pre_selection
    # For time-trace or z-plane .tif files, we process the data and create visualizations. Since these movies can have some time slots-of-interest, we load an extra excel table that allows a user to crop dat a of processed movies (or discard them at all). Note that the 'movie-I' field should match the above movie-IDs.
    import importlib
    importlib.reload(guv_io)
    selections_filename = "data_overview_Charu.xlsx"
    guv_users_df = guv_io.get_data_selections(selections_filename)

    if initval.suffix =='.tif'and initval.sequence=='time_trace':
        for mv_id, im_ori_name in enumerate(initval.movienames):
            fig, axs = plt.subplots(2, 3, figsize=(20, 15))
            source = initval.mainpath_out + initval.subdir_out + im_ori_name + initval.nc_name
            ds_guvs = xr.load_dataset(source)
            print(ds_guvs.info)

            #save a flattened file to excel for external use:

            df = ds_guvs.to_dataframe().reset_index()
            xls_target= initval.mainpath_out + initval.subdir_out + im_ori_name + initval.nc_name[:-4] + ".xlsx"
            df.to_excel(xls_target, index=False)



            for guv_id, this_guv in enumerate(ds_guvs["index"]):
                #check if guv was user_judged and if so, how
                mask = (
                        (guv_users_df["exp_id"] == initval.exp_id) &
                        (guv_users_df["movie_id"] == mv_id) &
                        (guv_users_df["guv_id"] == guv_id)
                )
                result = guv_users_df.loc[mask, "use"]
                if not result.empty:
                    user_okay = result.iloc[0]
                else:
                    user_okay = 1
                if  user_okay:
                    times = ds_guvs['index'].values
                    area = ds_guvs["Area"].sel(index=guv_id).values
                    c0_inside = ds_guvs["Inside_I"].sel(index=guv_id, channel=0).values
                    c0_outside = ds_guvs["Outside_I"].sel(index=guv_id, channel=0).values

                    sz = 4
                    # Plot various metrics
                    axs[0, 0].plot(area, 'o-', markersize=sz)
                    axs[0, 0].set_ylabel("area")
                    axs[0, 0].set_xlabel("time")
                    axs[0, 0].set_title("area")

                    axs[0, 1].plot(c0_inside, 'o-', markersize=sz)
                    axs[0, 1].set_ylabel("I, a.u.")
                    axs[0, 1].set_xlabel("time")
                    axs[0, 1].set_title("color0_inside")

                    axs[0, 2].plot(c0_outside, 'o-', markersize=sz)
                    axs[0, 2].set_ylabel("I, a.u.")
                    axs[0, 2].set_xlabel("time")
                    axs[0, 2].set_title("color0_outside")

                    plt.tight_layout()

if __name__ == "__main__":
    main()

