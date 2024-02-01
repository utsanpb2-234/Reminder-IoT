#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from paho.mqtt import client as mqtt_client

# mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883
topic = "test/rfid"
client_id = "rfid_pi"

# connect to mqtt broker
client = mqtt_client.Client(client_id)
client.connect(broker_ip, broker_port)
client.loop_start()

reader = SimpleMFRC522()

try:
    print("Ctrl + C to exit")
    while True:
        id, text = reader.read()
        print(f"UID: \t{id}")
        print(f"Content: \t{text}\n")
        client.publish(topic, f"{id}-{text}")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()

client.loop_stop()