import json
import pickle
import os
import numpy as np
import tensorflow as tf
import time
import sys


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


def process_data(features, labels, label_encoder):
    
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
    encoded_label_list = label_encoder(label_list)
    return feature_list, encoded_label_list


def build_dataset(feature_list, label_list, batch_size=16, shuffle=False):
    """Create a tf.data.Dataset from feature and label lists."""
    # convert to tensors
    feature_tensor = tf.constant(feature_list)

    # expand one dimension
    feature_tensor = tf.expand_dims(feature_tensor, axis=-1)
    
    label_tensor = tf.constant(label_list)
    
    # create TensorFlow dataset
    dataset = tf.data.Dataset.from_tensor_slices((feature_tensor, label_tensor))
    
    if shuffle:
        dataset = dataset.shuffle(buffer_size=len(feature_list))
    
    dataset = dataset.batch(batch_size)
    
    return dataset


def design_model(input_shape, num_output):
    model = tf.keras.Sequential([
        # Input layer and first convolutional layer
        tf.keras.layers.InputLayer(shape=input_shape),  # Input shape: (height, width, channels)
        
        # First convolutional layer with 32 filters, kernel size (3, 3), and 'SAME' padding
        tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu'),
        
        # Pooling layer (optional to reduce spatial size)
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), padding='same'),

        # Second convolutional layer with 32 filters, kernel size (3, 3), and 'SAME' padding
        tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu'),
        
        # Pooling layer (optional to reduce spatial size)
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), padding='same'),
        
        # Flatten layer to convert 2D feature maps to 1D vector
        tf.keras.layers.Flatten(),
        
        # Fully connected layer with 128 neurons (optional)
        tf.keras.layers.Dense(128, activation='relu'),
        
        # Output layer with 6 neurons (for 6 classes), using softmax activation for classification
        tf.keras.layers.Dense(num_output, activation='softmax')
    ])

    return model


def train_model_position(dataset_folder_list, label_encoder, input_shape=(15,140,1), batch_size=16, epoch=20, shuffle=True):

    # load multiple data files and merge into one object
    features, labels = load_multi_data(dataset_folder_list)
    
    # process data
    feature_list, label_list = process_data(features, labels, label_encoder)

    # build dataset (tf.data.dataset)
    dataset = build_dataset(feature_list, label_list, batch_size=batch_size, shuffle=shuffle)

    # split dataset into train and val
    train_size = int(len(dataset)*0.8)
    train_set = dataset.take(train_size)
    valid_set = dataset.skip(train_size)

    print(f"whole set has: {len(dataset)} batches when batch size is: {batch_size}")
    print(f"train set has: {len(train_set)} batches when batch size is: {batch_size}")
    print(f"valid set has: {len(valid_set)} batches when batch size is: {batch_size}")

    # define the model
    model = design_model(input_shape=input_shape, num_output=len(label_encoder.get_vocabulary()))

    # compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    model.summary()

    # train the model
    model.fit(train_set, validation_data=valid_set, epochs=epoch)

    # return model
    return model
    

if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # data folder
    folder_name_list = ["20241109_4", "20241109_6", "20241109_8"]
    folder_list = [os.path.join(data_dir, folder_name) for folder_name in folder_name_list]

    # dataset folder
    dataset_folder_list = [os.path.join(folder, "dataset") for folder in folder_list]

    ### sensor order ###
    # The height sensor array that is located to outside of the door should put first
    sensor_order = ['height1.csv', 'height2.csv', 'thermal1.csv', 'tof1.csv', 'thermal2.csv', 'tof2.csv']
    ### sensor order ### 

    # label encoder
    possible_labels = ["empty", "door_in", "door_out", "sink", "toilet", "other"]
    label_encoder = tf.keras.layers.StringLookup(vocabulary=possible_labels, output_mode='one_hot')
    
    # Save the label_encoder (StringLookup) object using pickle
    label_encoder_path = f'{file_dir}/label_encoder.pkl'

    with open(label_encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)

    print("Label encoder saved!")

    model = train_model_position(dataset_folder_list, label_encoder=label_encoder, input_shape=(15, 140, 1), batch_size=16, epoch=20, shuffle=False)

    # save model
    model_path = f'{file_dir}/cnn_model.keras'
    model.save(model_path)
    print(f"Model saved to: {model_path}")


