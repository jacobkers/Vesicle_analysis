This code analyzes movies of vesicles - 2023 onwards
Contents:
- description code A-series: GUV analysis
- description code B-series: analysis of fusion events on a flat membrane

# code 'A' series: GUV analysis with Rafa / Charu


## Step by step:
### ImageJ Drift vector
* Open imageJ
* Set measurement: include 'position in stack' (X, Y, Frame)
* Open BF or Phase
* Select "square" ROI and select a representative GUV
* Follow it at regular intervals with CTRL-M
* with FOV jumps, make sure you measure before-and after jump

### ImageJ area selection
* Open imageJ
* Open BF or Phase
* Select "round" ROI (keep Shift pressed for a circle)
* Find the position and press ALT"T" to load it into the ROI manager (check "show all" box)
* Click into the ROI manager window and CTRL+A to select all ROIs
* CLick More>list>File>Save As> ".....csv"
* for convenience, you might just save the screenshots with overlays

### Python
The code is divided in separate blocks that run one after another.
* A00 sets up a new experiment
* A10 
	- cuts the movie to standardized tiffs per guv
	- if provided, allows for drift correction
* A20a gets the geometry numbers
* A20b works on intensities
* A30 bundles results for ROIs


### notes
* to see binarization performance when tuning in a new dataset: A20 set frames to 1, binary-ops showit=1, run in debug mode 
* check the write-up:

