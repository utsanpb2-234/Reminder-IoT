from paho.mqtt import client as mqtt_client
import numpy as np
import time
import base64
import io
import matplotlib.pyplot as plt
from multiprocessing import Process
import numpy as np
import tensorflow as tf
import os
import pickle


height1 = [[1 for i in range(5)]] * 15
height2 = [[1 for i in range(5)]] * 15
thermal1 = [[0 for i in range(64)]] * 15
tof1 = [[1 for i in range(1)]] * 15
thermal2 = [[0 for i in range(64)]] * 15
tof2 = [[1 for i in range(1)]] * 15


def scale(data_str, max_value, min_value):
    data_list = data_str.split(",")
    data_list = [max(min(float(x),max_value), min_value)/max_value for x in data_list]
    return data_list

# call backs
def tof1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    max_value = 710*2
    min_value = 0

    tof1.append(scale(msg, max_value, min_value))
    
    while len(tof1) > 15:
        tof1.pop(0)
    

def tof2_handler(client, userdata, message):
    max_value = 560*2
    min_value = 0
    msg = message.payload.decode("utf-8")

    tof2.append(scale(msg, max_value, min_value))
    
    while len(tof2) > 15:
        tof2.pop(0)


def height1_handler(client, userdata, message):
    max_value = 610*2
    min_value = 0
    msg = message.payload.decode("utf-8")

    height1.append(scale(msg, max_value, min_value))
    
    while len(height1) > 15:
        height1.pop(0)


def height2_handler(client, userdata, message):
    max_value = 610*2
    min_value = 0
    msg = message.payload.decode("utf-8")

    height2.append(scale(msg, max_value, min_value))
    
    while len(height2) > 15:
        height2.pop(0)


def thermal1_handler(client, userdata, message):
    max_value = 35
    min_value = 20
    msg = message.payload.decode("utf-8")

    thermal1.append(scale(msg, max_value, min_value))
    
    while len(thermal1) > 15:
        thermal1.pop(0)


def thermal2_handler(client, userdata, message):
    max_value = 35
    min_value = 20
    msg = message.payload.decode("utf-8")

    thermal2.append(scale(msg, max_value, min_value))
    
    while len(thermal2) > 15:
        thermal2.pop(0)


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

    ### sensor order ###
    # The height sensor array that is located to outside of the door should put first
    sensor_order = ['height1.csv', 'height2.csv', 'thermal1.csv', 'tof1.csv', 'thermal2.csv', 'tof2.csv']
    ### sensor order ###

    # mqtt info
    broker_ip = "192.168.0.102"
    broker_port = 1883
    client_id = "python_client"

    client = mqtt_client.Client(callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1, client_id=client_id)
    client.message_callback_add("test/tof1", tof1_handler)
    client.message_callback_add("test/tof2", tof2_handler)
    client.message_callback_add("test/height1", height1_handler)
    client.message_callback_add("test/height2", height2_handler)
    client.message_callback_add("test/thermal1", thermal1_handler)
    client.message_callback_add("test/thermal2", thermal2_handler)

    client.connect(broker_ip, broker_port)
    client.subscribe("test/#")

    client.loop_start()
    time.sleep(4)

    try:
        while True:
            data_slice = [np.array(height1.copy()),
                          np.array(height2.copy()),
                          np.array(thermal1.copy()),
                          np.array(tof1.copy()),
                          np.array(thermal2.copy()),
                          np.array(tof2.copy())]
            
            data_sample = np.hstack(data_slice)
            data_expanded = np.expand_dims(data_sample, axis=0)  # expand batch
            data_expanded = np.expand_dims(data_expanded, axis=-1) # expand channel

            predicted_probs = loaded_model.predict(data_expanded, verbose=0)
            predicted_class = np.argmax(predicted_probs, axis=1)

            # Decode the predicted class back to the original label
            decoded_label = [label_encoder.get_vocabulary()[i] for i in predicted_class]
            print(f"Predicted_class: {predicted_class}. Predicted Label: {decoded_label}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        client.loop_stop()
        print("Inference stopped")
