# plot figures for each session with a specific window size
# and save the dataset into pkl files
import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as axes
from matplotlib.patches import Rectangle
import pandas as pd
from record_config import sensors_info, restroom_info
from data_record import Sensor
import pickle


def dataSlice(data, start, end):
    new_data = data[(data["time"] >= start) & (data["time"] <= end)]
    return new_data.copy()


def tof_plot_single(ax:axes.Axes, data:pd.DataFrame, duration, filename, time_start, button_data):
    data = data.iloc[:, 1].values
    feq = round(len(data)/duration)
    
    x = [i/feq for i in range(len(data))]

    ax.plot(x, data)
    ax.set_ylim(0, 1)
    ax.set_title(filename)

    # handle button info
    if len(button_data) > 0:
        for index, row in button_data.iterrows():
            ax.axvline(x=float(row["time"]-time_start), color=row["button"])


def thermal_plot_mesh(ax:axes.Axes, data:pd.DataFrame, duration, filename, time_start, button_data):
    data = data.iloc[:, 1:].values.transpose()
    feq = round(data.shape[1]/duration)

    xgrid = [(i+0.5)/feq for i in range(data.shape[1])]
    ygrid = [i+0.5 for i in range(data.shape[0])]
    
    ax.pcolormesh(xgrid, ygrid, data, vmin=0, vmax=1)
    ax.set_title(filename)

    # handle button info
    if len(button_data) > 0:
        for index, row in button_data.iterrows():
            ax.axvline(x=float(row["time"]-time_start), color=row["button"])


def tof_plot_mesh(ax:axes.Axes, data:pd.DataFrame, duration, filename, time_start, button_data):
    data = data.iloc[:, 1:].values.transpose()
    feq = round(data.shape[1]/duration)

    xgrid = [(i+0.5)/feq for i in range(data.shape[1])]
    ygrid = [i+0.5 for i in range(data.shape[0])]
    
    ax.pcolormesh(xgrid, ygrid, data, vmin=0, vmax=1)
    ax.set_title(filename)

    # handle button info
    if len(button_data) > 0:
        for index, row in button_data.iterrows():
            ax.axvline(x=float(row["time"]-time_start), color=row["button"])


plot_type_dict = {
    Sensor.tof_single: tof_plot_single,
    Sensor.thermal: thermal_plot_mesh,
    Sensor.tof_penta: tof_plot_mesh,
}


def patch_rectangle(ax:axes.Axes, x, y, width, height):
    rectangle = Rectangle((x, y), width, height, edgecolor='red', facecolor='none', linewidth=1)

    # Add the rectangle to the axis
    ax.add_patch(rectangle)


patch_rectangle_dict = {
    Sensor.tof_single: 1,
    Sensor.thermal: 64,
    Sensor.tof_penta: 5,
}


def scale(data:pd.DataFrame, filename):
    column_list = []
    max_value = 8192
    min_value = 0
    ## deal with different files
    # door sensor
    if "height" in filename:
        column_list = [f"tof{i}" for i in range(5)]
        max_value = restroom_info["door_width"]*2
    # toilet sensor
    elif filename == "tof1.csv":
        column_list = ["tof"]
        max_value = restroom_info["toilet_depth"]*2
    # sink sensor
    elif filename == "tof2.csv":
        column_list = ["tof"]
        max_value = restroom_info["sink_depth"]*2
    # thermal
    elif "thermal" in filename:
        column_list = [f"thermal{i}" for i in range(64)]
        max_value = 35
        min_value = 20

    for column in column_list:

        data[column] = data[column].apply(lambda x: max(min(x,max_value), min_value)/max_value)
    
    return data


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


def plot_main(data_list, type_list, file_list, title, time_start, time_end, pic_folder, button_data=[]):
    
    num_modal = len(data_list)

    plot_ratio = 0.2
    sub_plot_width = 8
    sub_plot_height = sub_plot_width*plot_ratio*num_modal
    
    duration = time_end - time_start

    # create canvas
    fig, ax = plt.subplots(nrows=num_modal, figsize=(sub_plot_width,sub_plot_height), sharex=True)
    
    # plot subplot
    for i in range(num_modal):
        plot_type_dict[type_list[i]](ax[i], data_list[i], duration, file_list[i], time_start, button_data)

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(f"{os.path.join(pic_folder, title)}.png", dpi=600)
    plt.close()


def plot_sub(data_list, type_list, file_list, title, time_start, time_end, pic_folder, button_data, window_size=3):
    
    num_modal = len(data_list)

    plot_ratio = 0.2
    sub_plot_width = 8
    sub_plot_height = sub_plot_width*plot_ratio*num_modal
   
    num_sample = min([len(data) for data in data_list])
    duration = time_end - time_start
    feq = round(num_sample/duration)
    window_len = window_size*feq

    session_dataset = {}

    for idx in range(0, num_sample+1-window_len):
        sub_data_list = [data.iloc[idx:idx+window_len,:] for data in data_list]
        sub_time_start = data_list[0].iloc[idx]["time"]
        
        # create canvas
        fig, ax = plt.subplots(nrows=num_modal, ncols=2, figsize=(sub_plot_width,sub_plot_height), sharex="col", gridspec_kw={'width_ratios': [2, 1]})
        
        # plot subplot and generate dataset dict
        dataset_dict = {}
        for i in range(num_modal):
            dataset_dict[file_list[i]] = sub_data_list[i]
            
            # draw overall figure
            plot_type_dict[type_list[i]](ax[i,0], data_list[i], duration, file_list[i], time_start, button_data)

            # patch rectangle to show the partial data area
            patch_rectangle(ax[i,0], x=idx/feq, y=0, width=window_size, height=patch_rectangle_dict[type_list[i]])
            
            # draw partial data
            plot_type_dict[type_list[i]](ax[i,1], sub_data_list[i], window_size, file_list[i], sub_time_start, button_data=[])

        fig.suptitle(f"{title}_{idx}")
        plt.tight_layout()
        plt.savefig(f"{os.path.join(pic_folder, title)}_{idx}.png", dpi=600)
        plt.close()

        #  dataset to session_dataset
        session_dataset[f"{title}_{idx}"] = dataset_dict
    
    return session_dataset


if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # data folder
    folder_name = "20250207_0"
    window_size = 3
    folder = os.path.join(data_dir, folder_name)

    # pic folder
    pic_folder = os.path.join(folder, "pics")
        
    if not os.path.exists(pic_folder):
        print(f"create folder {pic_folder}")
        os.mkdir(pic_folder)

    # dataset folder
    dataset_folder = os.path.join(folder, "dataset")
    
    # dataset folder guard
    if not os.path.exists(dataset_folder):
        print(f"create folder {dataset_folder}")
        os.mkdir(dataset_folder)

    # lists storing info
    sensor_files = []
    sensor_types = []
    sensor_data = []

    # handle button info separately
    button_file = None
    button_data = None

    for sensor_port in sensors_info.keys():
        filename = sensors_info[sensor_port][0]

        # button info stored alone
        if "button" in filename:
            button_file = filename
            button_data = pd.read_csv(os.path.join(folder, button_file))
            continue
        
        # store info
        sensor_files.append(filename)
        sensor_types.append(sensors_info[sensor_port][1])
        sensor_data.append(pd.read_csv(os.path.join(folder, filename)))
    
    num_modal = len(sensor_files)
    
    # case data
    case1_pd = pd.read_csv(os.path.join(folder, "case1.csv"), header=None)

    num_session = len(case1_pd)

    for session_id in range(num_session):
        
        session_name = case1_pd.iloc[session_id, 0]
        
        print(f"Processing {session_name}...", end="\t")

        time_start_str = case1_pd.iloc[session_id, 1]
        time_end_str = case1_pd.iloc[session_id, -1]

        time_start = np.floor(float(time_start_str[1:]))
        time_end = np.ceil(float(time_end_str[1:]))

        sensor_data_slice = []
        
        # slice for each modal
        for modal_id in range(num_modal):
            sensor_data_original = dataSlice(sensor_data[modal_id], time_start, time_end)
            sensor_data_processed = scale(sensor_data_original, sensor_files[modal_id])
            sensor_data_slice.append(sensor_data_processed)
        
        # handle sliced button info
        button_data_slice = None
        if button_file:
            button_data_slice = dataSlice(button_data, time_start, time_end)
        
        # plot the whole data in a session
        plot_main(sensor_data_slice, sensor_types, sensor_files, session_name, time_start, time_end, pic_folder, button_data_slice)

        # plot sub data in a session using sliding window
        # session folder
        session_folder = os.path.join(pic_folder, session_name)
            
        if not os.path.exists(session_folder):
            print(f"create folder {session_folder}")
            os.mkdir(session_folder)
        
        session_dataset = plot_sub(sensor_data_slice, sensor_types, sensor_files, session_name, time_start, time_end, session_folder, button_data_slice, window_size)
        
        # 'wb' mode is for writing in binary
        with open(f"{os.path.join(dataset_folder, session_name)}_feature.pkl", "wb") as file:  
            pickle.dump(session_dataset, file)

        print("Done.")
