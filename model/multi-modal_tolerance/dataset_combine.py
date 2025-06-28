# combine multiple pkl files into one, since the data split process is already done, we can directly combine the train and test data from multiple files.
# this is step three of the data preprocessing pipeline
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split


def load_and_combine_pkl_files(pkl_files):
    combined_feature = []
    combined_label = []


    for file in pkl_files:
        feature_file = f"{file}_feature.pkl" 
        label_file = f"{file}_label.pkl"

        # append feature
        with open(feature_file, 'rb') as f:
            data = pickle.load(f)
            print(f"Loaded feature data from {os.path.basename(feature_file)} with shape {data.shape}")
            combined_feature.append(data)

        # append label
        with open(label_file, 'rb') as f:
            data = pickle.load(f)
            print(f"Loaded label data from {os.path.basename(label_file)} with shape {data.shape}")
            combined_label.append(data)

    new_feature = np.concatenate(combined_feature, axis=0)
    new_label = np.concatenate(combined_label, axis=0)
    
    return new_feature, new_label

def save_to_pickle(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {file_path}")

def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print(f"Data loaded from {file_path} with shape {data.shape}")
    return data

def save_combined_data(X_train, X_test, y_train, y_test, file_path_prefix, overwrite=False):
    x_train_file_path = f"{file_path_prefix}_train_feature.pkl"
    x_test_file_path = f"{file_path_prefix}_test_feature.pkl"
    y_train_file_path = f"{file_path_prefix}_train_label.pkl"
    y_test_file_path = f"{file_path_prefix}_test_label.pkl"

    if os.path.exists(x_train_file_path) and not overwrite:
        print(f"{x_train_file_path} already exists! Set overwrite=True to overwrite.")
    else:
        save_to_pickle(X_train, x_train_file_path)
    
    if os.path.exists(x_test_file_path) and not overwrite:
        print(f"{x_test_file_path} already exists! Set overwrite=True to overwrite.")
    else:
        save_to_pickle(X_test, x_test_file_path)
    
    if os.path.exists(y_train_file_path) and not overwrite:
        print(f"{y_train_file_path} already exists! Set overwrite=True to overwrite.")
    else:
        save_to_pickle(y_train, y_train_file_path)
    
    if os.path.exists(y_test_file_path) and not overwrite:
        print(f"{y_test_file_path} already exists! Set overwrite=True to overwrite.")
    else:
        save_to_pickle(y_test, y_test_file_path)

def main(module_name, dataset_date, failure_type):
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_in_dir = os.path.join(file_dir, "splitted_dataset")
    data_out_dir = os.path.join(file_dir, "combined_dataset")

    # file names for different modules
    module_files = {
        "toilet": ["thermal1", "tof1"],
        "sink": ["thermal2", "tof2"],
        "door": ["height1", "height2"],
    }

    # list for pkl files
    pkl_files = ["no_failure"]
    for file in module_files.get(module_name, []):
        pkl_files.append(f"{failure_type}_{file}.csv")

    print(f"pkl files to combine: {pkl_files}")

    out_prefix = f"{dataset_date}_{module_name}_module_{failure_type}"
    pkl_files = [os.path.join(data_in_dir, f"{dataset_date}_{file}") for file in pkl_files]
    
    # load and combine pkl files
    pkl_files_train = [f"{file}_train" for file in pkl_files]
    X_train, y_train = load_and_combine_pkl_files(pkl_files_train)
    
    pkl_files_test = [f"{file}_test" for file in pkl_files]
    X_test, y_test = load_and_combine_pkl_files(pkl_files_test)

    print(f"train feature data: {X_train.shape}")
    print(f"train label data: {y_train.shape}")
    print(f"test feature data: {X_test.shape}")
    print(f"test label data: {y_test.shape}")
    
    # save combined data
    if not os.path.exists(data_out_dir):
        os.makedirs(data_out_dir)
    
    save_combined_data(X_train, X_test, y_train, y_test, os.path.join(data_out_dir, out_prefix))
    print(f"Combined data saved to {data_out_dir} with prefix {out_prefix}")
    
if __name__ == "__main__":
    dataset_date = "20241109"
    module_name = "door"
    failure_types = ["data_pollution", "latency_mismatch", "sensor_failure"]
    for failure_type in failure_types:
        main(module_name, dataset_date, failure_type)
