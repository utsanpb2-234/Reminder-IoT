import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_process import dataSlice


def singleDataPlot(data, key, yrange):
    x = [i for i in range(len(data))]
    data_processed = []
    for j in data:
        if j > yrange[1]:
            data_processed.append(yrange[1])
        else:
            data_processed.append(j)
    plt.plot(x, data_processed)
    plt.title(key)
    plt.ylim(yrange[0], yrange[1])
    plt.savefig(key, dpi=600)
    plt.close()


def singleThermalDataPlot(data, key, yrange):
    x = [i for i in range(len(data))]
    plt.plot(x, data)
    plt.title(key)
    plt.ylim(yrange[0], yrange[1])
    plt.savefig(key, dpi=600)
    plt.close()


def fingerDataPlot(data, key, size=[80,80]):
    data_list = [list(row) for row in data.values]
    for idx, data_by_time in enumerate(data_list):
        prefix_key = key[:key.rfind(".")]
        title = f"{prefix_key}_{idx}.png"
        data2d = np.reshape(data_by_time[1:], (size[0], size[1]))
        plt.imshow(data2d)
        plt.title(title)
        plt.savefig(title, dpi=600)
        plt.close()


if __name__ == "__main__":
    folder = "20240928_8"
    
    case1_file = os.path.join(folder, "case1.csv")
    # finger1_file = os.path.join(folder, "finger1.csv")
    height1_file = os.path.join(folder, "height1.csv")
    height2_file = os.path.join(folder, "height2.csv")
    thermal1_file = os.path.join(folder, "thermal1.csv")
    tof1_file = os.path.join(folder, "tof1.csv")
    # tof2_file = os.path.join(folder, "tof2.csv")

    case1_pd = pd.read_csv(case1_file, header=None)
    # finger1_pd = pd.read_csv(finger1_file)
    height1_pd = pd.read_csv(height1_file)
    height2_pd = pd.read_csv(height2_file)
    thermal1_pd = pd.read_csv(thermal1_file)
    tof1_pd = pd.read_csv(tof1_file)
    # tof2_pd = pd.read_csv(tof2_file)

    n = len(case1_pd)

    for i in range(n):
        
        sub_folder = os.path.join(folder, case1_pd.iloc[i, 0])
        
        if not os.path.exists(sub_folder):
            print(f"create folder {sub_folder}")
            os.mkdir(sub_folder)
        print(f"Processing {sub_folder}...", end="\t")
        time_start_str = case1_pd.iloc[i, 1]
        time_end_str = case1_pd.iloc[i, -1]

        time_start = np.floor(float(time_start_str[1:]))
        time_end = np.ceil(float(time_end_str[1:]))

        # new_finger1 = dataSlice(finger1_pd, time_start, time_end)
        new_height1 = dataSlice(height1_pd, time_start, time_end)
        new_height2 = dataSlice(height2_pd, time_start, time_end)
        new_thermal1 = dataSlice(thermal1_pd, time_start, time_end)
        new_tof1 = dataSlice(tof1_pd, time_start, time_end)
        # new_tof2 = dataSlice(tof2_pd, time_start, time_end)
        
        try:
            new_thermal1_max = []
            for i in range(len(new_thermal1)):
                new_thermal1_max.append(max(new_thermal1.iloc[i,1:].astype(np.float32)))
            singleThermalDataPlot(new_thermal1_max, f"{sub_folder}/thermal1max.png", [10, 30])
        except:
            pass

        singleDataPlot(new_tof1["tof"].values, f"{sub_folder}/tof1.png", [0, 2000])
        # singleDataPlot(new_tof2["tof"].values, f"{sub_folder}/tof2.png", [0, 2000])
        singleDataPlot(new_height1["tof0"].values, f"{sub_folder}/height1tof0.png", [0, 2000])
        singleDataPlot(new_height1["tof1"].values, f"{sub_folder}/height1tof1.png", [0, 2000])
        singleDataPlot(new_height1["tof2"].values, f"{sub_folder}/height1tof2.png", [0, 2000])
        singleDataPlot(new_height1["tof3"].values, f"{sub_folder}/height1tof3.png", [0, 2000])
        singleDataPlot(new_height1["tof4"].values, f"{sub_folder}/height1tof4.png", [0, 2000])
        singleDataPlot(new_height2["tof0"].values, f"{sub_folder}/height2tof0.png", [0, 2000])
        singleDataPlot(new_height2["tof1"].values, f"{sub_folder}/height2tof1.png", [0, 2000])
        singleDataPlot(new_height2["tof2"].values, f"{sub_folder}/height2tof2.png", [0, 2000])
        singleDataPlot(new_height2["tof3"].values, f"{sub_folder}/height2tof3.png", [0, 2000])
        singleDataPlot(new_height2["tof4"].values, f"{sub_folder}/height2tof4.png", [0, 2000])
        # fingerDataPlot(new_finger1, f"{sub_folder}/finger1.png", [80, 80])

        print("Done.")
