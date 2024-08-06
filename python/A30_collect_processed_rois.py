"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import csv
from pathlib import Path
from A00_init import get_exps

""" 
experiment indices (int = laptop, add: 0.1 for office local, 0.2 to run on CD:K:):
0: .nd testfiles
1: .lif testfiles
2: .tif testfiles (only laptop)
3: .tif test (office-PC) less_challenging ones

"""
expi = 5.2   #2: flexibles; 3:less_challenging ones 4: single-image tiffs
initval = get_exps(expi)


# X	Y	R_minor	R_major	color0_inside	c0_edge	c0_outside	color1_inside	c1_edge	c1_outside	color2_inside	c2_edge	c2_outside	color3_inside	c3_edge	c3_outside

name=[]
X=[]
Y=[]
data=[]
if initval.suffix =='.tif'and initval.sequence=='single_frame':
    load_dirname=initval.mainpath_out + initval.subdir +str("/A20b_processed/")
    csv_path_in = Path(load_dirname)
    for csv_source in csv_path_in.glob("**/*.csv"):  # find all csv files in inpath
        print(csv_source.stem)
        with open(csv_source) as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                name.append(csv_source.stem)
                data.append(row)

 #set up csv for tracking data:
csv_path_out = Path(initval.mainpath_out + initval.subdir +str("/A30_processed/"))
if not csv_path_out.is_dir():
        csv_path_out.mkdir()
        
csv_target=load_dirname  + "collected_data" + str(".csv")
with open(csv_target, "w",newline='') as csv_f:  # will overwrite existing
    # create the csv writer
    writer = csv.writer(csv_f, delimiter=";")
    #f = open("test.csv", "a")
    writer.writerow(row.keys())
    for data_row in data:  
        
        # create the csv writer
        writer = csv.writer(csv_f, delimiter=";")
        #f = open("test.csv", "a")
        writer.writerow(data_row.values()) 
    dum=1
    