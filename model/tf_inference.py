import numpy as np
import tensorflow as tf
import os
import pickle

if __name__ == "__main__":
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # load the model and perform inference
    loaded_model = tf.keras.models.load_model(f'{file_dir}/cnn_model.keras')

    label_encoder_path = f'{file_dir}/label_encoder.pkl'
    f = open(label_encoder_path, "rb")
    label_encoder = pickle.load(f)
    f.close()

    test_feature = np.random.rand(1, 15, 140, 1)
    print(test_feature.shape)
    predicted_probs = loaded_model.predict(test_feature)
    predicted_class = np.argmax(predicted_probs, axis=1)

    print(f"predicted_class: {predicted_class}")

    # Decode the predicted class back to the original label
    decoded_label = [label_encoder.get_vocabulary()[i] for i in predicted_class]
    print(f"Predicted Label: {decoded_label}")