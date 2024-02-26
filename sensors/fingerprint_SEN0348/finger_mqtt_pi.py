import serial
import numpy as np
import time
from paho.mqtt import client as mqtt_client
import base64
import io
import matplotlib.pyplot as plt


width = 80
height = 80
ser = serial.Serial("/dev/ttyACM0", 115200, timeout=4)

# mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883
topic = "test/finger1"
topic_demo = "test/finger1_demo"
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
            # send raw data
            client.publish(topic, data)

            # send based64 picture
            # convert data to 2d array first
            data = data.split(",")
            data = [int(i) for i in data]
            data = np.reshape(data, (width, height))

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
            client.publish(topic_demo, pic_hash)
except KeyboardInterrupt:
    ser.close()
    print("\nserial closed.")
    client.loop_stop()
    print("mqtt client closed.")
