import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, accuracy_score
import os
import pickle
import numpy as np
import argparse
import sys

tf.keras.utils.set_random_seed(1)
np.random.seed(1)

def load_pickle_data(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

def parse_label(data_str, keyword):
    return 1 if data_str == keyword else 0

def extract_feature_label(feature_list, label_list, keyword, data_indics):
    tof_feature = []
    thermal_feature = []
    label = []
    module_files = {
        "toilet": ["thermal1", "tof1"],
        "sink": ["thermal2", "tof2"],
        "door": ["height1", "height2"],
    }
    for i in range(len(feature_list)):
        tof_feature.append(feature_list[i][:, data_indics[f"{module_files[keyword][1]}.csv"][0]:data_indics[f"{module_files[keyword][1]}.csv"][1]])
        thermal_feature.append(feature_list[i][:, data_indics[f"{module_files[keyword][0]}.csv"][0]:data_indics[f"{module_files[keyword][0]}.csv"][1]])
        label.append(parse_label(label_list[i], keyword))
    return np.array(tof_feature), np.array(thermal_feature), np.array(label)

def base_model_performance(model, label_encoder, feature, label, keyword):
    labels = [i for i in range(7)]
    decoded_labels = [label_encoder.get_vocabulary()[labels[i]] for i in range(7)]

    predictions = model.predict(feature, verbose=2)
    pred_labels = np.argmax(predictions, axis=1)
    true_labels = np.argmax(label_encoder(label), axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(true_labels, pred_labels, average=None, labels=labels[1:])
    conf_matrix = confusion_matrix(true_labels, pred_labels, labels=labels[1:])
    print()
    print(f"Base model on {keyword}: Per-class metrics:")
    print("class & precision & recall & F1-score & support")
    for i, class_label in enumerate(decoded_labels[1:]):
        print(f"{class_label} & {precision[i]:.4f} & {recall[i]:.4f} & {f1[i]:.4f} & {support[i]}")

    test_loss, test_acc = model.evaluate(feature, label_encoder(label), verbose=2)
    class_acc = accuracy_score(true_labels, pred_labels)
    print(f"Base model on {keyword} Test class accuracy: {class_acc:.4f}")
    print(f"Base model on {keyword} Test accuracy: {test_acc:.4f}")
    print(f"Base model on {keyword} Test loss: {test_loss:.4f}")
    print()

    return precision, recall, f1, support, conf_matrix, test_loss, test_acc

def multi_modal_performance(model, feature, label, keyword, threshold=0.5):
    predictions = model.predict(feature, verbose=2)
    pred_labels = (predictions > threshold).astype(int).flatten()
    true_labels = label
    precision, recall, f1, support = precision_recall_fscore_support(true_labels, pred_labels, average='binary')
    print()
    print(f"Multi-modal model on {keyword}:  metrics:")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")

    test_loss, test_acc = model.evaluate(feature, label, verbose=2)
    class_acc = accuracy_score(true_labels, pred_labels)
    print(f"Multi-modal model on {keyword} Test class accuracy: {class_acc:.4f}")
    print(f"Multi-modal model on {keyword} Test accuracy: {test_acc:.4f}")
    print(f"Multi-modal model on {keyword} Test loss: {test_loss:.4f}")
    print()

    return precision, recall, f1, support, test_loss, test_acc


def main(target_model, target_dataset, verify_type, module_name, dataset_date):

    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    
    dataset_path = os.path.join(file_dir, target_dataset)
    model_path = os.path.join(parent_dir, target_model)

    # results_dir = os.path.join(file_dir, "results", dataset_name)
    
    # # create results directory if it does not exist
    # if not os.path.exists(results_dir):
    #     os.makedirs(results_dir)
    # # else add appropriate suffix to avoid overwriting
    # else:
    #     suffix = 1
    #     while os.path.exists(f"{results_dir}_{suffix}"):
    #         suffix += 1
    #     results_dir = f"{results_dir}_{suffix}"
    #     os.makedirs(results_dir)
    # print(f"Results will be saved in: {results_dir}")

    # # save print output to a file
    # log_std_file = os.path.join(results_dir, "output_std.log")
    # sys.stdout = open(log_std_file, "w")
    # log_err_file = os.path.join(results_dir, "output_err.log")
    # sys.stderr = open(log_err_file, "w")
    # print(f"Running multi-modal model for {module_name} on {dataset_date} with failure type {failure_type}")

    data_indics = {
        "height1.csv": [0,5],
        "height2.csv": [5,10],
        "thermal1.csv": [10,74],
        "tof1.csv": [74,75],
        "thermal2.csv": [75,139],
        "tof2.csv": [139,140],
    }

    # load data
    print("Loading test data...")
    test_feature = load_pickle_data(f"{dataset_path}_test_feature.pkl")
    test_label = load_pickle_data(f"{dataset_path}_test_label.pkl")
    print("Data loaded successfully.")

    # load base model for evaluation
    print("Loading model...")
    print(f"Model path: {model_path}")
    model = tf.keras.models.load_model(model_path)
    print(model.summary())
    print(f"Model loaded. {target_model}")

    # evaluate data
    if verify_type == "multi_modal":
        # extract features and labels for the specified module
        tof_test, thermal_test, label_test = extract_feature_label(test_feature, test_label, module_name, data_indics)
        
        # print dataset shapes
        print(f"Testing TOF feature shape: {tof_test.shape}")
        print(f"Testing Thermal feature shape: {thermal_test.shape}")
        print(f"Testing label shape: {label_test.shape}")
        result = multi_modal_performance(model, [tof_test, thermal_test], label_test, "cross test multi-modal data")
    elif verify_type == "base_model":
        label_encoder_path = os.path.join(parent_dir, f"{dataset_date}_label_encoder.pkl")
        label_encoder = load_pickle_data(label_encoder_path)
        result = base_model_performance(model, label_encoder, test_feature, test_label, "cross test base model data")

    return result[-1]
    

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Multi-modal model with selectable failure type and dataset.")

    # parser.add_argument("--module", type=str, required=True, help="sensor module name")
    # parser.add_argument("--dataset_date", type=str, required=True, help="dataset date")
    # parser.add_argument("--failure_type", type=str, required=True, help="failure type to evaluate")
    # args = parser.parse_args()

    # main(module_name=args.module, dataset_date=args.dataset_date, failure_type=args.failure_type)

    scenarios = ["20241109", "20250207"]
    locations = ["sink", "toilet"]
    tf.keras.config.enable_unsafe_deserialization()
    results = []

    for scenario1 in scenarios:
        for scenario2 in scenarios:
            for location1 in locations:
                for location2 in locations:
                    target_model = f"multi-modal_tolerance/results/{scenario1}_{location1}_module_data_pollution/multi_modal_model.keras"
                    target_dataset = f"combined_dataset/{scenario2}_{location2}_module_data_pollution"
                    verify_type = "multi_modal"
                    module_name = f"{location2}"
                    dataset_date = f"{scenario1}"
                    result = main(target_model, target_dataset, verify_type, module_name, dataset_date)
                    results.append(f"{scenario1}-{scenario2}-{location1}-{location2}: {result}")

    print("results:")
    for res in results:
        print(res)