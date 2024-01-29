#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time

reader = SimpleMFRC522()

try:
    print("Ctrl + C to exit")
    while True:
        id, text = reader.read()
        print(f"UID: \t{id}")
        print(f"Content: \t{text}\n")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()