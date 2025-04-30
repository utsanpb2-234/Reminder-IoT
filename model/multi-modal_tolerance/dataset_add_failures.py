# create dataset for multi-modal tolerance system
import json
import pickle
import os
import numpy as np
import tensorflow as tf
import time
import sys
from failure_simulation import simulate_sensor_failure, simulate_data_pollution, simulate_latency_mismatch
import random


tf.keras.utils.set_random_seed(1)

def load_single_data(feature_path, label_path):
    
    # load feature from pickle
    with open(feature_path, 'rb') as f:
        features = pickle.load(f)
    
    # load label from json
    with open(label_path, 'r') as f:
        labels = json.load(f)
    
    return features, labels

def load_multi_data(folder_list):
    
    # initialize dicts
    features_total = {}
    labels_total = {}
    
    # for loop to traverse all folders
    for folder in folder_list:
        for file in sorted(os.listdir(folder)):
            # find interested file
            if file.endswith("feature.pkl"):
                
                # generate interested paths
                feature_path = os.path.join(folder, file)
                label_path = os.path.join(folder, file.replace("feature.pkl", "label_by_frame.json"))
                
                # load single data feature-label pair
                feature_single, label_single = load_single_data(feature_path=feature_path, label_path=label_path)

                # update to the total data feature-label pair
                features_total.update(feature_single)
                labels_total.update(label_single)
    
    return features_total, labels_total

def process_data(features, labels):
    
    # common keys
    keys = features.keys() & labels.keys()
    
    # process features
    feature_list = []

    for idx, k in enumerate(keys):
        # initiate an empty list
        numpy_list = []
        
        # append numpy arry to list by order
        for id_model, modal in enumerate(sensor_order):
            numpy_list.append(features[k][modal].iloc[:,1:].to_numpy())

        # stack the numpy arrays into one feature, use hstack along columns
        feature_list.append(np.hstack(numpy_list))

    # process labels
    label_list = [labels[k] for idx, k in enumerate(keys)]

    return np.array(feature_list), np.array(label_list)

def dump2pickle(feature_list, label_list, file_path_prefix, overwrite=False):
   
    feature_path = f"{file_path_prefix}_feature.pkl"
    if os.path.exists(feature_path) and not overwrite:
        print(f"{feature_path} already exists! Set overwrite=True to overwrite.")
    else:
        with open(feature_path, 'wb') as f:
            pickle.dump(feature_list, f)
        print(f"{feature_path} is saved!")
    
    label_path = f"{file_path_prefix}_label.pkl"
    if os.path.exists(label_path) and not overwrite:
        print(f"{label_path} already exists! Set overwrite=True to overwrite.")
    else:
        with open(label_path, 'wb') as f:
            pickle.dump(label_list, f)
        print(f"{label_path} is saved!")

def add_instant_failure(features, labels, failure_type, chosen_modal):
    feature_list = features.copy()
    label_list = labels.copy()
    
    failure_function = None
    if failure_type == "sensor_failure":
        failure_function = simulate_sensor_failure
    elif failure_type == "data_pollution":
        failure_function = simulate_data_pollution
    else:
        raise ValueError("Invalid failure type. Choose between 'sensor_failure' and 'data_pollution'.")

    for idx in range(len(feature_list)):
        
        # get current data
        cur_data = feature_list[idx, : , data_indics[chosen_modal][0]:data_indics[chosen_modal][1]]

        # update data by applying failure function
        feature_list[idx, : , data_indics[chosen_modal][0]:data_indics[chosen_modal][1]] = failure_function(cur_data)

    return feature_list, label_list

def add_latency_failure(features, labels, chosen_modal):
    feature_list = features.copy()
    label_list = labels.copy()

    for idx in range(len(feature_list)-1, 0, -1):
        
        # get current data
        cur_data = feature_list[idx, : , data_indics[chosen_modal][0]:data_indics[chosen_modal][1]]

        prev_data = feature_list[idx-1, : , data_indics[chosen_modal][0]:data_indics[chosen_modal][1]]

        # update data by applying failure function
        feature_list[idx, : , data_indics[chosen_modal][0]:data_indics[chosen_modal][1]] = simulate_latency_mismatch(cur_data=cur_data, prev_data=prev_data)

    return feature_list, label_list


if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    root_dir = os.path.dirname(parent_dir)

    # data root dir
    data_root_dir = os.path.join(root_dir, "data")
    
    # data folder
    folder_name_list = ["20241109_4", "20241109_6", "20241109_8"]
    dataset_prefix = "20241109"
    folder_list = [os.path.join(data_root_dir, folder_name) for folder_name in folder_name_list]
    
    # dataset folder
    dataset_folder_list = [os.path.join(folder, "dataset") for folder in folder_list]

    features, labels = load_multi_data(dataset_folder_list)

    ### sensor order ###
    # The height sensor array that is located to outside of the door should put first
    sensor_order = ['height1.csv', 'height2.csv', 'thermal1.csv', 'tof1.csv', 'thermal2.csv', 'tof2.csv']
    ### sensor order ###
    data_indics = {
        "height1.csv": [0,5],
        "height2.csv": [5,10],
        "thermal1.csv": [10,74],
        "tof1.csv": [74,75],
        "thermal2.csv": [75,139],
        "tof2.csv": [139,140],
    }

    # load label encoder
    label_encoder_path = f'{file_dir}/label_encoder.pkl'
    f = open(label_encoder_path, "rb")
    label_encoder = pickle.load(f)
    f.close()

    # process data
    feature_list, label_list = process_data(features, labels)
    
    data_output_path = os.path.join(file_dir, "dataset")
    if not os.path.exists(data_output_path):
        os.makedirs(data_output_path)
    
    # save no failure features and labels
    dump2pickle(feature_list, label_list, os.path.join(data_output_path, f"{dataset_prefix}_no_failure"))


    # failure for each modal
    for modal in sensor_order:
        print(f"no failure feature {modal}: {feature_list[:3,:,data_indics[modal][0]:data_indics[modal][1]]}")
        print(f"no failure label: {label_list[:3]}")
        # sensor failure
        failed_feature, failed_label = add_instant_failure(feature_list, label_list, failure_type="sensor_failure", chosen_modal=modal)
        print(f"failed_feature {modal}: {failed_feature[:3,:,data_indics[modal][0]:data_indics[modal][1]]}")
        print(f"failed_label: {failed_label[:3]}")
        dump2pickle(failed_feature, failed_label, os.path.join(data_output_path, f"{dataset_prefix}_sensor_failure_{modal}"))

        # data pollution
        polluted_feature, polluted_label = add_instant_failure(feature_list, label_list, failure_type="data_pollution", chosen_modal=modal)
        print(f"polluted feature {modal}: {polluted_feature[:3,:,data_indics[modal][0]:data_indics[modal][1]]}")
        print(f"polluted label: {polluted_label[:3]}")
        dump2pickle(polluted_feature, polluted_label, os.path.join(data_output_path, f"{dataset_prefix}_data_pollution_{modal}"))

        # latency mismatch
        latency_feature, latency_label = add_latency_failure(feature_list, label_list, chosen_modal=modal)
        print(f"latency feature {modal}: {latency_feature[:3,:,data_indics[modal][0]:data_indics[modal][1]]}")
        print(f"latency label: {latency_label[:3]}")
        dump2pickle(latency_feature, latency_label, os.path.join(data_output_path, f"{dataset_prefix}_latency_mismatch_{modal}"))
