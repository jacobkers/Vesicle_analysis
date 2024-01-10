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


# overview of experiments:
def get_exps():
    Exp1 = Guv_experiment()
    Exp1.subdir = str("60 uM_1h incubation/")
    Exp1.movienames = ["1", "2", "3", "16", "9"]  # the ones that have ROIs measured in ImageJ

    Experiments = [Exp1]

    return Experiments
