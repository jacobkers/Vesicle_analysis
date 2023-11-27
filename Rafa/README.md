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
	* for quick testing, set 'init.skips'>1 
* open 'A10_guvalyzer_shell'
	* select your new case to run
	* check/uncheck the 'if 0's to skip time-consuming steps (NB: first time, always run A20-25). 
	* run it. Typically, you might have to correct typos in the config.
