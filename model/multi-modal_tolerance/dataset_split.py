# split each dataset file into train and test sets, this keeps the data preprocessing pipeline modular and allows for easy integration with other steps in the pipeline.
# this is step two of the data preprocessing pipeline
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split


def split_data(feature_list, label_list, test_size=0.2):
    X_train, X_test, y_train, y_test = train_test_split(
        feature_list, label_list, test_size=test_size, random_state=42, shuffle=True)
    
    return X_train, X_test, y_train, y_test

def save_to_pickle(data, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {file_path}")

def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print(f"Data loaded from {file_path} with shape {data.shape}")
    return data

if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_in_dir = os.path.join(file_dir, "dataset")
    data_out_dir = os.path.join(file_dir, "splitted_dataset")

    files = os.listdir(data_in_dir)

    data_prefix = "20250207"

    for file in files:
        if file.startswith(data_prefix) and file.endswith("_feature.pkl"):
            print(f"Processing file: {file}")
            feature_file = os.path.join(data_in_dir, file)
            label_file = os.path.join(data_in_dir, file.replace("_feature.pkl", "_label.pkl"))

            # Load feature and label data
            feature_data = load_from_pickle(feature_file)
            label_data = load_from_pickle(label_file)

            # Split data
            X_train, X_test, y_train, y_test = split_data(feature_data, label_data)

            # Save splitted data
            save_to_pickle(X_train, os.path.join(data_out_dir, file.replace("_feature.pkl", "_train_feature.pkl")))
            save_to_pickle(X_test, os.path.join(data_out_dir, file.replace("_feature.pkl", "_test_feature.pkl")))
            save_to_pickle(y_train, os.path.join(data_out_dir, file.replace("_feature.pkl", "_train_label.pkl")))
            save_to_pickle(y_test, os.path.join(data_out_dir, file.replace("_feature.pkl", "_test_label.pkl")))
