from record_config import *
from file_ops import writeFile
from data_record import Sensor
from paho.mqtt import client as mqtt_client
import serial
import numpy as np
import time
import base64
import io
import matplotlib.pyplot as plt
from multiprocessing import Process


# global mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883


# data transform functions:
def finger_to_base64(data):
    data = data.split(",")
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
    return data


sensorDataTransform = {
    Sensor.tof_single: do_nothing,
    Sensor.thermal: do_nothing,
    Sensor.finger: finger_to_base64,
    Sensor.mic: do_nothing,
    Sensor.tof_penta: do_nothing,
}


def dataMQTT(port=None, topic=None, client_id=None, sensorType=None):
    ser = serial.Serial(port, 115200, timeout=4)

    client = mqtt_client.Client(client_id)
    client.connect(broker_ip, broker_port)
    client.loop_start()

    print(f"start publishing...{topic}")
    try:
        while True:
            if ser.in_waiting:
                data = ser.readline()
                try:
                    data = data.decode("utf-8")[:-2]

                    # transform data based on sensor type
                    data = sensorDataTransform[sensorType](data)

                    client.publish(topic, data)
                except:
                    print(f"{topic}: pass one error reading.")
                    pass
    except KeyboardInterrupt:
        ser.close()
        print(f"stopped publish...{topic}")
        client.loop_stop()


if __name__ == "__main__":
    
    for sensor_port in sensors_info_mqtt.keys():
        sensor_thread = Process(target=dataMQTT, daemon=True, args=(sensor_port, sensors_info_mqtt[sensor_port][0], sensors_info_mqtt[sensor_port][1], sensors_info_mqtt[sensor_port][2],))
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