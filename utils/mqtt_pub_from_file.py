# monitor data from file and publish to mqtt broker
# each sensor has its own process
from record_config import *
from file_ops import writeFile
from data_record import Sensor
from paho.mqtt import client as mqtt_client
import serial
import serial.tools
import serial.tools.list_ports
import numpy as np
import time
import base64
import io
import matplotlib.pyplot as plt
from multiprocessing import Process
from record_config import sensors_info, sensors_info_mqtt
import os
from sh import tail


# global mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883


# data transform functions:
def finger_to_base64(data):
    data = data.split(",")[1:]
    data = [int(i) for i in data]
    data = np.reshape(data, (80, 80))

    # draw picture
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5,5))
    ax.imshow(data)
    pic_IObytes = io.BytesIO()

    # save to IO
    fig.savefig(pic_IObytes,  format='png')
    plt.close(fig)

    # based64 picture and send to mqtt broker
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())

    return pic_hash


def do_nothing(data):
    data_list = data.split(",")[1:]
    data = ",".join(data_list)
    return data


sensorDataTransform = {
    Sensor.tof_single: do_nothing,
    Sensor.thermal: do_nothing,
    Sensor.finger: finger_to_base64,
    Sensor.mic: do_nothing,
    Sensor.tof_penta: do_nothing,
    Sensor.button: do_nothing,
}


def dataMQTT(filename=None, topic=None, client_id=None, sensorType=None):

    client = mqtt_client.Client(client_id)
    client.connect(broker_ip, broker_port)
    client.loop_start()

    print(f"Start publishing...{topic}")
    try:
        while True:
            try:
                for line in tail("-f", filename, _iter=True):

                    # transform data based on sensor type
                    data = sensorDataTransform[sensorType](line)

                    client.publish(topic, data)
                    
            except Exception as e:
                print(e)
            finally:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"Stopped publishing...{topic}")
        client.loop_stop()


if __name__ == "__main__":
    # folder path
    folder = "20240928_8"
    
    # read one file one process
    for sensor_port in sensors_info_mqtt.keys():
        filename = os.path.join(folder, sensors_info[sensor_port][0])
        sensor_thread = Process(target=dataMQTT, daemon=True, args=(filename, sensors_info_mqtt[sensor_port][0], sensors_info_mqtt[sensor_port][1], sensors_info_mqtt[sensor_port][2],))
        sensor_thread.start()
    
    time.sleep(1)

    while True:
        cmd = input("enter q to quit: ")
        if cmd == "q":
            break
        else:
            print("no input or unrecognized cmd")
            continue

    time.sleep(2)
