# GUV analysis with Rafael De Lira 
2023 onwards

## Step by step:

### ImageJ area selection
* Open imageJ
* Open BF or Phase
* Select "round" ROI (keep Shift pressed for a circle)
* Find the position and press "T" to load it into the ROI manager (check "show all" box)
* Click into the ROI manager window and CTRL+A to select all ROIs
* CLick More>list>File>Save As> "ROI.csv"
* for convenience, you might just save ascreenshots with overlays

### Matlab
* open 'A000_get_config.m'
* check 'case 0' carefully to see how in and out paths, names are defined (see the comments per setting)
* copy, make a new 'case' and adapt accordingly
* for quick testing, adapt 'init.skips' (processes only one in n frames)
* open 'A10_guvalyzer_shell'
* selct your new case to run
* check/uncheck the 'if 0's to skip time-consuming steps (NB: first time, run always A20-25)
* run it. Typically, you might have to correct typos in the config.
