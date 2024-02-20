# -*- coding: utf-8 -*-
"""
31-12-2022
@author: jkerssemakers
"""


class Guv_experiment:
    """
    sets paths, names
    """
    def __init__(self):
        self.mainpath_in = str(
            "M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.mainpath_out = str(
            "M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/Rafa/Test Rafa_Nikon microscope/DOPC.DOPS/"
        )
        self.subdir = str()
        self.movienames = []
        self.suffix='tif'

# overview of experiments:
def get_exps(exp_idx):
    Exp1 = Guv_experiment()
    Exp1.mainpath_in=str(
            "D:/jkerssemakers/CD_Data_in/2023_Rafa/DOPC.DOPS/"
        )
    Exp1.mainpath_out = str(
            "D:/jkerssemakers/Dropbox\CD_Data_out/2023_Rafael/DOPC.DOPS/"
        )
    Exp1.subdir = str("60 uM_1h incubation/")
    Exp1.movienames = ["1", "2", "3", "16", "9"]  # the ones that have ROIs measured in ImageJ
    Exp1.suffix='.nd2'

    Exp2 = Guv_experiment()
    Exp2.mainpath_in="M:/tnw/bn/cd\Shared/Jacob/TESTdata_in/Rafa/Test Rafa_Lif/"
    Exp2.mainpath_out="M:/tnw/bn/cd\Shared/Jacob/TESTdata_out/Rafa/Test Rafa_Lif/"
    Exp2.subdir = str("Test_subdir/")
    Exp2.movienames = ["40mMLUVs_WITHCerC6"]  # the ones that have ROIs measured in ImageJ
    Exp2.suffix='.lif'


    all_Experiments = [Exp1, Exp2]

    Experiment = all_Experiments[exp_idx]

    return Experiment
