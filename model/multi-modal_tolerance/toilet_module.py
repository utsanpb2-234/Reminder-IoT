import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import os
import pickle
import numpy as np


tf.keras.utils.set_random_seed(1)

def load_pickle_data(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

# ============ Subnet: Self-Assessment (for each sensor) ============
def build_self_assessment_subnet(input_shape):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Flatten(),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # Output health score [0,1]
    ])
    return model

# ============ Subnet: Object Detection (for each sensor) ============
def build_detection_subnet(input_shape):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # Output detection score [0,1]
    ])
    return model

# ============ Full Multi-Modal Model ============
def build_multi_modal_model(tof_input_shape, thermal_input_shape):
    # Inputs
    tof_input = layers.Input(shape=tof_input_shape, name="tof_input")
    thermal_input = layers.Input(shape=thermal_input_shape, name="thermal_input")

    # Each sensor has its own Self-Assessment and Detection subnetwork
    tof_self_assess = build_self_assessment_subnet(tof_input_shape)(tof_input)      # Output: scalar
    thermal_self_assess = build_self_assessment_subnet(thermal_input_shape)(thermal_input)

    tof_detect = build_detection_subnet(tof_input_shape)(tof_input)                 # Output: scalar
    thermal_detect = build_detection_subnet(thermal_input_shape)(thermal_input)

    # Concatenate assessment + detection for each sensor
    tof_features = layers.Concatenate()([tof_self_assess, tof_detect])  # Shape (2,)
    thermal_features = layers.Concatenate()([thermal_self_assess, thermal_detect])  # Shape (2,)

    # Concatenate both sensors' features
    fused_features = layers.Concatenate()([tof_features, thermal_features])  # Shape (4,)

    # Attention Layer: learn weight between ToF and Thermal
    attention_logits = layers.Dense(2)(fused_features)  # (batch_size, 2)
    attention_weights = layers.Softmax()(attention_logits)  # Normalize

    # Split attention weights
    tof_weight = layers.Lambda(lambda x: x[:, 0:1])(attention_weights)   # (batch_size, 1)
    thermal_weight = layers.Lambda(lambda x: x[:, 1:2])(attention_weights)

    # Weighted sum of detection outputs
    final_detection = tof_weight * tof_detect + thermal_weight * thermal_detect

    # Optionally, squeeze to scalar
    final_output = layers.Flatten()(final_detection)

    # Define model
    model = models.Model(inputs=[tof_input, thermal_input], outputs=final_output)

    return model

def parse_label(data_str):
    if data_str == "toilet":
        return 1
    else:
        return 0

def extract_feature_label(feature_list, label_list):
    tof_feature = []
    thermal_feature = []
    label = []
    for i in range(len(feature_list)):
        tof_feature.append(feature_list[i][:, data_indics["tof1.csv"][0]:data_indics["tof1.csv"][1]])
        thermal_feature.append(feature_list[i][:, data_indics["thermal1.csv"][0]:data_indics["thermal1.csv"][1]])
        label.append(parse_label(label_list[i]))
    
    return np.array(tof_feature), np.array(thermal_feature), np.array(label)

if __name__ == "__main__":
    #  data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)

    data_dir = os.path.join(file_dir, "combined_dataset")
    data_prefix = "20241109_toilet_module"

    # load data
    train_feature = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_train_feature.pkl"))
    train_label = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_train_label.pkl"))
    test_feature = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_test_feature.pkl"))
    test_label = load_pickle_data(os.path.join(data_dir, f"{data_prefix}_test_label.pkl"))

    data_indics = {
        "height1.csv": [0,5],
        "height2.csv": [5,10],
        "thermal1.csv": [10,74],
        "tof1.csv": [74,75],
        "thermal2.csv": [75,139],
        "tof2.csv": [139,140],
    }

    # extract tof modal, thermal modal, and label
    tof_train, thermal_train, label_train = extract_feature_label(train_feature, train_label)
    print(tof_train.shape)
    print(thermal_train.shape)
    print(label_train.shape)

    model = build_multi_modal_model(tof_input_shape=(15,), thermal_input_shape=(15,64))
    print(model.summary())
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit([tof_train, thermal_train], label_train, batch_size=32, epochs=1)

    # evaluate the model
    test_tof, test_thermal, label_test = extract_feature_label(test_feature, test_label)
    test_loss, test_acc = model.evaluate([test_tof, test_thermal], label_test)

    # evaluate the base model
    print(test_feature.shape)
    print(test_label.shape)
    base_model_path = os.path.join(parent_dir, "cnn_model.keras")
    
    label_encoder_path = os.path.join(parent_dir, "label_encoder.pkl")
    f = open(label_encoder_path, "rb")
    label_encoder = pickle.load(f)
    f.close()

    base_model = tf.keras.models.load_model(base_model_path)
    print(base_model.summary())
    
    base_test_loss, base_test_acc = base_model.evaluate(test_feature, label_encoder(test_label))

    no_failure_feature = load_pickle_data(os.path.join(file_dir, "dataset", f"20241109_no_failure_feature.pkl"))
    no_failure_label = load_pickle_data(os.path.join(file_dir, "dataset", f"20241109_no_failure_label.pkl"))
    no_failure_tof, no_failure_thermal, label_no_failure = extract_feature_label(no_failure_feature, no_failure_label)

    no_failure_loss, no_failure_acc = model.evaluate([no_failure_tof, no_failure_thermal], label_no_failure)
    base_model_loss, base_model_acc = base_model.evaluate(no_failure_feature, label_encoder(no_failure_label))
    
    print(f"Failure data: Base model accuracy: {base_test_acc}")
    print(f"Failure data: Base model loss: {base_test_loss}")
    print(f"Failure data: Multi-modal model accuracy: {test_acc}")
    print(f"Failure data: Multi-modal model loss: {test_loss}")
    print(f"Normal data: Base model accuracy: {base_model_acc}")
    print(f"Normal data: Base model loss: {base_model_loss}")
    print(f"Normal data: Multi-modal model accuracy: {no_failure_acc}")
    print(f"Normal data: Multi-modal model loss: {no_failure_loss}")

    labels = [i for i in range(7)]
    decoded_labels = [label_encoder.get_vocabulary()[labels[i]] for i in range(7)]

    pred_failure = base_model.predict(test_feature)
    pred_normal = base_model.predict(no_failure_feature)

    base_y_pred = np.argmax(pred_failure, axis=1)
    base_y_true = np.argmax(label_encoder(test_label), axis=1)
    print(base_y_pred.shape)
    print(base_y_true.shape)
    precision, recall, f1, support = precision_recall_fscore_support(base_y_true, base_y_pred, average=None, labels=labels[1:])
    conf_matrix = confusion_matrix(base_y_true, base_y_pred, labels=labels[1:])
    print("\nFailure data: Per-class metrics:")
    print("class & precision & recall & F1-score & support")
    for i, class_label in enumerate(decoded_labels[1:]):
        print(f"{class_label} & {precision[i]:.4f} & {recall[i]:.4f} & {f1[i]:.4f} & {support[i]}")

    base_y_pred = np.argmax(pred_normal, axis=1)
    base_y_true = np.argmax(label_encoder(no_failure_label), axis=1)
    print(base_y_pred.shape)
    print(base_y_true.shape)
    precision, recall, f1, support = precision_recall_fscore_support(base_y_true, base_y_pred, average=None, labels=labels[1:])
    conf_matrix = confusion_matrix(base_y_true, base_y_pred, labels=labels[1:])
    print("\nNormal data: Per-class metrics:")
    print("class & precision & recall & F1-score & support")
    for i, class_label in enumerate(decoded_labels[1:]):
        print(f"{class_label} & {precision[i]:.4f} & {recall[i]:.4f} & {f1[i]:.4f} & {support[i]}")