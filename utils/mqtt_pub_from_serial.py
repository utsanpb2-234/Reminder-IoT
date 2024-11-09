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
    Sensor.button: do_nothing,
}


def find_device_by_serial(usb_serial, topic):
    while True:
        device_list = serial.tools.list_ports.comports()
        for device in device_list:
            if device.serial_number == usb_serial:
                print(f"Found device {usb_serial} on {device.device}")
                return device.device
        
        print(f"Did not find device: {topic}-{usb_serial}, try again after 5 seconds")
        time.sleep(5)


def connect(usb_serial, topic):
    serial_port = find_device_by_serial(usb_serial, topic)
    ser = serial.Serial(serial_port, 115200, timeout=4)
    print(f"Connected {serial_port}")
    return ser


def dataMQTT(usb_serial=None, topic=None, client_id=None, sensorType=None):
    ser = connect(usb_serial, topic)

    client = mqtt_client.Client(client_id)
    client.connect(broker_ip, broker_port)
    client.loop_start()

    print(f"Start publishing...{topic}")
    try:
        while True:
            try:
                if ser.in_waiting:
                    data = ser.readline()
                    try:
                        data = data.decode("utf-8")[:-2]

                        # transform data based on sensor type
                        data = sensorDataTransform[sensorType](data)

                        client.publish(topic, data)
                    except Exception as e:
                        print(f"{topic}: pass one error reading.")
                        pass
            except Exception as e:
                print(e)
                print("Lost connection, reconnecting...")
                ser = connect(usb_serial, topic)
    except KeyboardInterrupt:
        ser.close()
        print(f"Stopped publishing...{topic}")
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
