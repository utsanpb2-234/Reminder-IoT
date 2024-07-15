import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from file_ops import writeFileFromList


def dataSlice(data, start, end):
    new_data = data[(data["time"] >= start) & (data["time"] <= end)]
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


def detectedHeight(height1, threshold = 500):
    if any(height1) < threshold:
        return True
    else:
        return False


def isDuring(time, range):
    if range[0] < time <= range[1]:
        return True
    else:
        return False


def most_frequent(List):
    counter = 0
    num = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
 
    return num


def activity_sequence_embeddings(data, activity_window_size):
    activity_timestamp = []
    activity_in_seconds = []
    activity_sequence = []

    for _, value in enumerate(data):
        activity_timestamp.append([value[0], float(value[1:])])
    
    time_start = np.floor(activity_timestamp[0][1])
    time_end = np.ceil(activity_timestamp[-1][1])
    # print(f"time duration: {time_end - time_start} seconds.")
    
    # first three seconds will be "s" by default
    activity_in_seconds.extend(["s", "s", "s"])

    time_cur = time_start + activity_window_size

    while time_cur <= time_end - activity_window_size:
        for idx in range(len(activity_timestamp) - 1):
            if isDuring(time_cur, [activity_timestamp[idx][1], activity_timestamp[idx+1][1]]):
                activity_in_seconds.append(activity_timestamp[idx][0])
                break
        
        time_cur += 1

    # last three second will be "e" by default
    activity_in_seconds.extend(["e", "e", "e"])

    i = 0

    while i < len(activity_in_seconds):
        activity_sequence.append(most_frequent(activity_in_seconds[i:i+activity_window_size]))
        i += activity_window_size
    
    # print(f"activity in seconds: {len(activity_in_seconds)}, activity in window size: {len(activity_sequence)}")
    # print(activity_sequence)
    return activity_sequence

if __name__ == "__main__":
    folders = ["../data/20240415_0",
               "../data/20240415_1",
               "../data/20240415_2",
               "../data/20240415_3",
               ]
    
    dataset_filename = "dataset.csv"

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

            # extract relative time duration
            height1_slice = dataSlice(height1_pd, time_start, time_end)
            thermal1_slice = dataSlice(thermal1_pd, time_start, time_end)
            tof1_slice = dataSlice(tof1_pd, time_start, time_end)
            tof2_slice = dataSlice(tof2_pd, time_start, time_end)

            tof1_embedded = tof_embeddings(tof1_slice)
            tof2_embedded = tof_embeddings(tof2_slice)
            height1_embedded = height1_embeddings(height1_slice)
            thermal1_embedded = thermal1_embeddings(thermal1_slice)

            writeFileFromList(dataset_filename, tof1_embedded, "a")
            writeFileFromList(dataset_filename, tof2_embedded, "a")
            writeFileFromList(dataset_filename, height1_embedded, "a")
            writeFileFromList(dataset_filename, thermal1_embedded, "a")

            print("Done.")

    print("\nAll cases are processed")