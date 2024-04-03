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


class dataMQTT():
    def __init__(self, port=None, topic=None, client_id=None, sensorType=None) -> None:
        self.port = port
        self.sensorType = sensorType

        # open serial port
        self.ser = serial.Serial(self.port, 115200, timeout=4)

        
        self.topic = topic
        self.client_id = client_id

        # connect to mqtt broker
        self.client = mqtt_client.Client(self.client_id)
        self.client.connect(broker_ip, broker_port)
        self.client.loop_start()

    def run(self):
        print(f"start publishing...{self.topic}")
        try:
            while True:
                if self.ser.in_waiting:
                    data = self.ser.readline()
                    try:
                        data = data.decode("utf-8")[:-2]

                        # transform data based on sensor type
                        data_transformed = sensorDataTransform[self.sensorType](data)
                        
                        self.client.publish(self.topic, data_transformed)
                    except:
                        print(f"{self.topic}: pass one error reading.")
                        pass
        except KeyboardInterrupt:
            self.ser.close()
            print(f"stopped publish...{self.topic}")
            self.client.loop_stop()


if __name__ == "__main__":
    
    for sensor_port in sensors_info_mqtt.keys():
        sensor = dataMQTT(sensor_port, sensors_info_mqtt[sensor_port][0], sensors_info_mqtt[sensor_port][1], sensors_info_mqtt[sensor_port][2])
        sensor_thread = Process(target=sensor.run, daemon=True)
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