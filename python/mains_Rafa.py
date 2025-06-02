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
#from Rafa import B00_membrane_fusion_event_detector
if 1:
    from Rafa import B00_init
    from Rafa import B00_membrane_fusion_event_detector
    from Rafa import B10_membrane_fusion_kymograph_generator
    from Rafa import B20_membrane_fusion_analyzer
    from Rafa import B30_membrane_fusion_analyzer_user_additions
    from Rafa import B35_collect_all_and_user_additions
    from Rafa import B40_load_and_plot

if __name__ == "__main__":
    print("Running from vesicles directory:")
    exps=B00_init.get_exps()
    if 0: B00_membrane_fusion_event_detector.detect(exps)
    if 0: B10_membrane_fusion_kymograph_generator.kymo(exps)
    #for the following, events should be as yet manually classified
    if 0: B20_membrane_fusion_analyzer.fusion(exps)
    if 0: B30_membrane_fusion_analyzer_user_additions.click_them(exps)
    if 0: B35_collect_all_and_user_additions.collect_them(exps)
    if 1: B40_load_and_plot.collect_them(exps)