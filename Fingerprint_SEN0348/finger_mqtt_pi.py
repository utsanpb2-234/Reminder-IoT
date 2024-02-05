import serial
import time
import numpy as np
import time
from paho.mqtt import client as mqtt_client

ser = serial.Serial("/dev/tty.usbmodem11101", 115200, timeout=4)

# mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883
topic = "test/finger1"
client_id = "finger1_pi"

# connect to mqtt broker
client = mqtt_client.Client(client_id)
client.connect(broker_ip, broker_port)
client.loop_start()

try:
    while True:
        if ser.in_waiting:
            data = ser.readline()
            data = data.decode("utf-8")[:-2]
            data = data.split(",")
            print(data)
            client.publish(topic, data)
except KeyboardInterrupt:
    ser.close()
    print("\nserial closed.")
    client.loop_stop()
    print("mqtt client closed.")
    