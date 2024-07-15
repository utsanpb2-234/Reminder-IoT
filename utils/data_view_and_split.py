import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from file_ops import writeFileFromList


def dataSlice(data, start, end):
    new_data = data[(data["time"] > start) & (data["time"] <= end)]
    return new_data


def tof_embeddings(df, threshold=2000):
    
    data_list = df["tof"].values
    data_filtered = [min(i, threshold) for i in data_list]
    
    return [data_filtered]
    

def height1_embeddings(df, threshold=2000):
    result = [[] for i in range(5)]
    keys = ["tof0", "tof1", "tof2", "tof3", "tof4"]
    for i in range(5):
        data_list = df[keys[i]].values
        result[i] = [min(j, threshold) for j in data_list]

    return result


def thermal1_embeddings(df):
    result = [[] for i in range(64)]
    keys = [f"thermal{i}" for i in range(64)]
    for i in range(64):
        result[i] = df[keys[i]].values
        
    return result

def data_pad_or_cut(data, desired_len):

    new_data = []
    for _, data_row in enumerate(data):
        while len(data_row) > desired_len:
            data_row.pop(-1)
        
        length = len(data_row)

        for i in range(length, desired_len):
            data_row = np.append(data_row, data_row[-1])
        
        new_data.append(data_row)

    return new_data

def preview_time_window(tof1_data, tof2_data, height1_data):
    fig, ax = plt.subplots(nrows=7, figsize=(21,6), sharex=True)
    x = range(len(tof1_data[0]))
    ax[0].plot(x, tof1_data[0], label="tof1")
    ax[1].plot(x, tof2_data[0], label="tof2")
    ax[2].plot(x, height1_data[0], label="height0")
    ax[3].plot(x, height1_data[1], label="height1")
    ax[4].plot(x, height1_data[2], label="height2")
    ax[5].plot(x, height1_data[3], label="height3")
    ax[6].plot(x, height1_data[4], label="height4")
    for i in range(7):
        ax[i].set_ylim(bottom=0, top=2000)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    folders = ["../data/20240415_0",
               "../data/20240415_1",
               "../data/20240415_2",
               "../data/20240415_3",
               ]
    
    time_window = 3
    freq = 5

    dataset_filename = f"dataset_{time_window}s.csv"
    label_filename = f"label_{time_window}s.csv"
    activities_filename = f"activities.csv"

    activity_sequence = []

    for folder in folders:
        # input files
        case1_file = os.path.join(folder, "case1.csv")
        height1_file = os.path.join(folder, "height1.csv")
        thermal1_file = os.path.join(folder, "thermal1.csv")
        tof1_file = os.path.join(folder, "tof1.csv")
        tof2_file = os.path.join(folder, "tof2.csv")

        # read csv files
        case1_pd = pd.read_csv(case1_file, header=None)
        height1_pd = pd.read_csv(height1_file)
        thermal1_pd = pd.read_csv(thermal1_file)
        tof1_pd = pd.read_csv(tof1_file)
        tof2_pd = pd.read_csv(tof2_file)


        n = len(case1_pd)

        for i in range(n):

            print(f"Processing case: {case1_pd.iloc[i, 0]}...", end="\t")
            time_start_str = case1_pd.iloc[i, 1]
            time_end_str = case1_pd.iloc[i, -1]

            time_start = np.floor(float(time_start_str[1:]))
            time_end = np.ceil(float(time_end_str[1:]))

            time_cur = time_start

            sequence = []

            while time_cur < time_end:

                # extract relative time duration
                height1_slice = dataSlice(height1_pd, time_cur, time_cur+time_window)
                thermal1_slice = dataSlice(thermal1_pd, time_cur, time_cur+time_window)
                tof1_slice = dataSlice(tof1_pd, time_cur, time_cur+time_window)
                tof2_slice = dataSlice(tof2_pd, time_cur, time_cur+time_window)

                tof1_embedded = tof_embeddings(tof1_slice)
                tof2_embedded = tof_embeddings(tof2_slice)
                height1_embedded = height1_embeddings(height1_slice)
                thermal1_embedded = thermal1_embeddings(thermal1_slice)

                tof1_processed = data_pad_or_cut(tof1_embedded, time_window*freq)
                tof2_processed = data_pad_or_cut(tof2_embedded, time_window*freq)
                height1_processed = data_pad_or_cut(height1_embedded, time_window*freq)
                thermal1_processed = data_pad_or_cut(thermal1_embedded, time_window*freq)

                preview_time_window(tof1_processed, tof2_processed, height1_processed)

                writeFileFromList(dataset_filename, tof1_processed, "a")
                writeFileFromList(dataset_filename, tof2_processed, "a")
                writeFileFromList(dataset_filename, height1_processed, "a")
                writeFileFromList(dataset_filename, thermal1_processed, "a")

                activity_cur = input("current activity: ")

                sequence.append(activity_cur)

                time_cur += time_window

            writeFileFromList(label_filename, sequence, "a")

            activity_sequence.append(sequence)
            
            print("Done.")
    
    writeFileFromList(activities_filename, activity_sequence, "a")

    print("\nAll cases are processed")