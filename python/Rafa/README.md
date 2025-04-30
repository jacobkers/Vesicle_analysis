# GUV analysis with Rafael de Lira ('A' series)
2023 onwards



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
* A00 sets up a new experiment
* A10 
	- cuts the movie to standardized tiffs per guv
	- if provided, allows for drift correction
* A20a gets the geometry numbers
* A20b works on intensities
* A30 bundles results for ROIs



### notes
* to see binaryzation performance when tuning in a new dataset: A20 set frames to 1, binary-ops showit=1, run in debug mode 
* check the write-up:

# fusion analysis with Rafael de Lira ('B' series)
## Step by step:
### ImageJ: build particle image
Typcally, a STD projection works best (consider smoothing)

### Python
programs run via  mains_Rafa
* B00_init sets up a new experiment
* B00_membrane_fusion_event_detector: detects local spots in the 'particle image'
* B10_membrane_fusion_kymograph_generator: builds a time trace for every spot
* B20_membrane_fusion_analyzer: builds on the kymograps, exports timings and diffusion constants
* B30_membrane_fusion_analyzer_user_additions: allows click actions of the user to identify double releases etc.