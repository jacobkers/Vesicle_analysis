#set up local and import common tools
#customs:
import sys
import os
# Get the current working directory
current_directory = os.getcwd()
# Move one or two directories up
two_levels_up = os.path.abspath(os.path.join(current_directory, "..", ".."))
one_level_up = os.path.abspath(os.path.join(current_directory, ".."))
# Insert the path to sys.path
sys.path.insert(0, current_directory)

#import Rafa's
#from Rafa import B10_membrane_fusion_kymograph_generator
from Rafa import B20_membrane_fusion_analyzer

if __name__ == "__main__":
    print("Running from vesicles directory:")
    #B10_membrane_fusion_kymograph_generator.kymo()
    B20_membrane_fusion_analyzer.fusion()