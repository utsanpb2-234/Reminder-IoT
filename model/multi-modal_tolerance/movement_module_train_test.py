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

def build_self_assessment_subnet(input_shape):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Flatten(),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

def build_detection_subnet(input_shape):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(3, activation='softmax')
    ])
    return model

def build_multi_modal_model(module1_shape, module2_shape):
    m1_input = layers.Input(shape=module1_shape, name="module1_input")
    m2_input = layers.Input(shape=module2_shape, name="module2_input")

    m1_self_assess = build_self_assessment_subnet(module1_shape)(m1_input)
    m2_self_assess = build_self_assessment_subnet(module2_shape)(m2_input)

    m1_detect = build_detection_subnet(module1_shape)(m1_input)
    m2_detect = build_detection_subnet(module2_shape)(m2_input)

    m1_features = layers.Concatenate()([m1_self_assess, m1_detect])
    m2_features = layers.Concatenate()([m2_self_assess, m2_detect])

    fused_features = layers.Concatenate()([m1_features, m2_features])

    attention_logits = layers.Dense(2)(fused_features)
    attention_weights = layers.Softmax()(attention_logits)
    
    m1_weight = layers.Lambda(lambda x: x[:, 0:1])(attention_weights)
    m2_weight = layers.Lambda(lambda x: x[:, 1:2])(attention_weights)
    final_detection = m1_weight * m1_detect + m2_weight * m2_detect

    final_output = layers.Flatten()(final_detection)

    model = models.Model(inputs=[m1_input, m2_input], outputs=final_output)
    return model

def parse_label(data_str):
    if data_str == "door_in":
        return np.array([0,1,0])
    elif data_str == "door_out":
        return np.array([0,0,1])
    else:
        return np.array([1,0,0])

def extract_feature_label(feature_list, label_list, keyword, data_indics):
    m1_feature = []
    m2_feature = []
    label = []
    module_files = {
        "toilet": ["thermal1", "tof1"],
        "sink": ["thermal2", "tof2"],
        "door": ["height1", "height2"],
    }
    for i in range(len(feature_list)):
        m1_feature.append(feature_list[i][:, data_indics[f"{module_files[keyword][1]}.csv"][0]:data_indics[f"{module_files[keyword][1]}.csv"][1]])
        m2_feature.append(feature_list[i][:, data_indics[f"{module_files[keyword][0]}.csv"][0]:data_indics[f"{module_files[keyword][0]}.csv"][1]])
        label.append(parse_label(label_list[i]))
    return np.array(m1_feature), np.array(m2_feature), np.array(label)

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
    decoded_labels = ["other", "door_in", "door_out"]
    predictions = model.predict(feature, verbose=2)
    pred_labels = np.argmax(predictions, axis=1)
    true_labels = np.argmax(label, axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(true_labels, pred_labels, average=None)
    print()
    print(f"Multi-modal model on {keyword}:  metrics:")
    for i, class_label in enumerate(decoded_labels):
        print(f"{class_label} & {precision[i]:.4f} & {recall[i]:.4f} & {f1[i]:.4f} & {support[i]}")

    test_loss, test_acc = model.evaluate(feature, label, verbose=2)
    class_acc = accuracy_score(true_labels, pred_labels)
    print(f"Multi-modal model on {keyword} Test class accuracy: {class_acc:.4f}")
    print(f"Multi-modal model on {keyword} Test accuracy: {test_acc:.4f}")
    print(f"Multi-modal model on {keyword} Test loss: {test_loss:.4f}")
    print()

    return precision, recall, f1, support, test_loss, test_acc

def main(module_name, dataset_date, failure_type):
    dataset_name = f"{dataset_date}_{module_name}_module_{failure_type}"

    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    
    data_dir = os.path.join(file_dir, "combined_dataset")
    data_prefix = dataset_name

    results_dir = os.path.join(file_dir, "results", dataset_name)
    # create results directory if it does not exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    # else add appropriate suffix to avoid overwriting
    else:
        suffix = 1
        while os.path.exists(f"{results_dir}_{suffix}"):
            suffix += 1
        results_dir = f"{results_dir}_{suffix}"
        os.makedirs(results_dir)
    print(f"Results will be saved in: {results_dir}")

    # save print output to a file
    log_std_file = os.path.join(results_dir, "output_std.log")
    sys.stdout = open(log_std_file, "w")
    log_err_file = os.path.join(results_dir, "output_err.log")
    sys.stderr = open(log_err_file, "w")
    print(f"Running multi-modal model for {module_name} on {dataset_date} with failure type {failure_type}")

    data_indics = {
        "height1.csv": [0,5],
        "height2.csv": [5,10],
        "thermal1.csv": [10,74],
        "tof1.csv": [74,75],
        "thermal2.csv": [75,139],
        "tof2.csv": [139,140],
    }

    # load multimodal experiment data
    print("Loading data with failures...")
    train_feature = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_train_feature.pkl"))
    train_label = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_train_label.pkl"))
    test_feature = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_test_feature.pkl"))
    test_label = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_test_label.pkl"))
    print("Data with failures loaded successfully.")

    # load normal data
    print("Loading normal data...")
    normal_feature = load_pickle_data(os.path.join(file_dir, "splitted_dataset", "20241109_no_failure_test_feature.pkl"))
    normal_label = load_pickle_data(os.path.join(file_dir, "splitted_dataset", "20241109_no_failure_test_label.pkl"))
    print("Normal data loaded successfully.")

    # extract features and labels for the specified module
    m1_train, m2_train, label_train = extract_feature_label(train_feature, train_label, module_name, data_indics)
    m1_test, m2_test, label_test = extract_feature_label(test_feature, test_label, module_name, data_indics)
    m1_normal, m2_normal, label_normal = extract_feature_label(normal_feature, normal_label, module_name, data_indics)

    # print dataset shapes
    print(f"Training module 1 feature shape: {m1_train.shape}")
    print(f"Training module 2 feature shape: {m2_train.shape}")
    print(f"Training label shape: {label_train.shape}")
    print(f"Testing module 1 feature shape: {m1_test.shape}")
    print(f"Testing module 2 feature shape: {m2_test.shape}")
    print(f"Testing label shape: {label_test.shape}")
    print(f"Normal module 1 feature shape: {m1_normal.shape}")
    print(f"Normal module 2 feature shape: {m2_normal.shape}")
    print(f"Normal label shape: {label_normal.shape}")
    
    # train multi-modal model
    print("Training multi-modal model...")
    model = build_multi_modal_model(module1_shape=(15,5), module2_shape=(15,5))
    print(model.summary())
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit([m1_train, m2_train], label_train, batch_size=32, epochs=10, verbose=2)
    print("Multi-modal model training completed.")
    # save the trained model
    model_path = os.path.join(results_dir, f"{dataset_name}.keras")
    model.save(model_path)
    print(f"Trained model saved at: {model_path}")

    # load base model and label encoder for evaluation
    print("Loading base model and label encoder...")
    base_model_path = os.path.join(parent_dir, f"{dataset_date}_cnn_model.keras")
    base_model = tf.keras.models.load_model(base_model_path)
    label_encoder_path = os.path.join(parent_dir, f"{dataset_date}_label_encoder.pkl")
    label_encoder = load_pickle_data(label_encoder_path)
    print(base_model.summary())
    print(f"Base model and label encoder loaded. {base_model_path}, {label_encoder_path}")

    # evaluate data with failures
    multi_modal_performance(model, [m1_test, m2_test], label_test, "test data with failures")
    base_model_performance(base_model, label_encoder, test_feature, test_label, "test data with failures")

    # evaluate normal data
    multi_modal_performance(model, [m1_normal, m2_normal], label_normal, "normal data")
    base_model_performance(base_model, label_encoder, normal_feature, normal_label, "normal data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-modal model with selectable failure type and dataset.")

    parser.add_argument("--module", type=str, required=True, help="sensor module name")
    parser.add_argument("--dataset_date", type=str, required=True, help="dataset date")
    parser.add_argument("--failure_type", type=str, required=True, help="failure type to evaluate")
    args = parser.parse_args()

    main(module_name=args.module, dataset_date=args.dataset_date, failure_type=args.failure_type)
