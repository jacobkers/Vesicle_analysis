"""
21-2-2024
Work guv imagery
@author: jkerssemakers
"""
import csv
import numpy as np
from pathlib import Path
from A00_init import get_exps
import matplotlib.pyplot as plt

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


if initval.suffix =='.tif'and initval.sequence=='single_frame':
    #collect single-frame data points and re-save all in one file
    load_dirname=initval.mainpath_out + initval.subdir +str("/A20b_processed/")
    csv_path_in = Path(load_dirname)
    name=[]
    X=[]
    Y=[]
    data=[]
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
    

if initval.suffix =='.tif'and initval.sequence=='time_trace':
    fig, axs=plt.subplots(3,1)
     #collect files per trace:
    #collect single-frame data points and re-save all in one file
    
    load_dirname_A20a=initval.mainpath_out + initval.subdir +str("/A20a_tracked/")
    load_dirname_A20b=initval.mainpath_out + initval.subdir +str("/A20b_processed/")
    csv_path_in_A20a = Path(load_dirname_A20a)
    csv_path_in_A20b = Path(load_dirname_A20b)
    for csv_source in csv_path_in_A20a.glob("**/*.csv"):  # find all csv files in inpath
        name=[]
        data=[]
        data2=[]
        lab1=str(csv_source.stem)
        stri=lab1.find("_xy_tracked")
        lab2=lab1[0:stri]+('_all_data')
        csv_source2=Path(load_dirname_A20b + lab2+".csv")
        with open(csv_source) as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                name.append(lab1[0:stri])
                data.append(row)
        with open(csv_source2) as g:
            reader = csv.DictReader(g, delimiter=";")
            for row in reader:
                data2.append(row)
        #plotting
        R_ratio=[]
        R_minor=[]
        R_major=[]
        c0_edge=[]
        c1_edge=[]
        for row in data2:
            if float(row['R_minor'])>0:
                R_ratio.append(float(row['R_major'])/float(row['R_minor']))
            else:
                R_ratio.append(np.nan)
            R_minor.append(float(row['R_minor']))
            R_major.append(float(row['R_major']))
            c0_edge.append(float(row['c0_edge']))
            c1_edge.append(float(row['c1_edge']))
        axs[0].plot(c1_edge, R_ratio, 'o-')
        axs[1].plot(c0_edge)
        axs[2].plot(c1_edge)
    fig.show()
    dum=1