import serial
import numpy as np
import time
from paho.mqtt import client as mqtt_client
import base64
import io
import matplotlib.pyplot as plt
from file_ops import writeFile


# mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883
client_id = "python_client"

writeFile("tof1.csv", "", "w")
writeFile("tof2.csv", "","w")
writeFile("height1.csv", "", "w")
writeFile("thermal1.csv", "", "w")
writeFile("finger1.csv", "", "w")

# call backs
def tof1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("tof1.csv", msg, "a")

def tof2_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("tof2.csv", msg, "a")

def height1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("height1.csv", msg, "a")

def thermal1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("thermal1.csv", msg, "a")

def mic1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("mic1.csv", msg, "a")

def finger1_handler(client, userdata, message):
    msg = message.payload.decode("utf-8")
    msg = f"{time.time()},{msg}\n"
    writeFile("finger1.csv", msg, "a")

# connect to mqtt broker
client = mqtt_client.Client(client_id)
client.message_callback_add("test/tof1", tof1_handler)
client.message_callback_add("test/tof2", tof2_handler)
client.message_callback_add("test/height1", height1_handler)
client.message_callback_add("test/thermal1", thermal1_handler)
# client.message_callback_add("test/mic1", mic1_handler)
client.message_callback_add("test/finger1", finger1_handler)

client.connect(broker_ip, broker_port)
client.subscribe("test/#")

client.loop_start()

case_header = "case,start,end"
case_file = "cases.csv"

writeFile(case_header, case_file, "a")

while True:
    cmd = input("enter case number to start, or q to quit:")
    if cmd == "q":
        break
    else:
        time_start = time.time()
        input("enter to stop current case")
        time_stop = time.time()
        case_info = f"{cmd},{time_start},{time_stop}"
        writeFile(case_info, case_file, "a")

client.loop_stop()