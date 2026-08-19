Cees Dekker Lab, Bionanoscience department, TU Delft, 07/2026, 
developed by Jacob Kerssemakers and Bert Van Herck

# Installation (Python)

- Install miniconda from https://docs.conda.io/en/latest/miniconda.html 
- Open terminal (on Windows, search for 'Anaconda prompt')
- Install Git from https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
- Clone this repository with `git clone`
- Within a terminal, change directory into this repository (`cd mypath`, replace mypath with the directory in which environment.yml is located)
- Create the environment by executing `conda env create -f environment_vesicles.yml`
- Install the Python package by executing `pip install -e .`

# Execute Python files

- Activate the environment by executing `conda activate vesicles` in a terminal
- You can now run the GUI by executing `start_gui.py`

Alternatively, change the interpreter path of your IDE to the `vesicles` environment.
For Spyder, that can be done as follows:
- Go to Preferences
- Go to tab 'Python interpreter'
- Select 'Use the following Python interpreter'
- With Miniconda, the path to the Python interpreter will be as follows: `C:/Users/USERNAME/Miniconda3/envs/min_analysis/python.exe` (change `USERNAME` to your user)

# Remove environment (Python)

If you want to remove the environment (because you don't need it anymore or you want to recreate it), execute `conda env remove -n min_analysis` from the base environment.


Jacob Kerssemakers, 2026
