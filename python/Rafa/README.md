# GUV analysis with Rafael de Lira 
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
* A10 cuts the movie to standardized tiffs per guv
* A20a gets the geometry numbers
* A20b works on intensities



### notes
to see binaryzation performance when tuning in a new dataset: A20 set frames to 1, binary-ops showit=1, run in debug mode 