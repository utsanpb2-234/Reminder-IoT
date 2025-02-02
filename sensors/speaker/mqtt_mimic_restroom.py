import pygame
import time
from paho.mqtt import client as mqtt_client
import datetime
import logging
import os
os.environ['SDL_AUDIODRIVER'] = 'alsa'
import socket


# get basic info
file_dir = os.path.dirname(os.path.abspath(__file__))
script_name = os.path.splitext(os.path.basename(__file__))[0]

# set logger
logger = logging.getLogger(script_name)
logger.setLevel(logging.DEBUG)
log_filename = os.path.join(file_dir, f"{script_name}.log")
file_handler = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# pygame initialization
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

#pygame.mixer.init()

# sound file
toilet_file = os.path.join(file_dir, "audio_flush_toilet.wav")
#toilet_file = "audio_flush_toilet.wav"
toilet_sound = pygame.mixer.Sound(toilet_file)

sink_file = os.path.join(file_dir, "audio_wash_hands.wav")
#sink_file = "audio_wash_hands.wav"
sink_sound = pygame.mixer.Sound(sink_file)

# mqtt info
broker_ip = "192.168.0.146"
broker_port = 1883
topic = "test/button1"
client_id = f"speaker_{socket.gethostname()}"
print (client_id)

# callback
def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8").strip()
    logger.info(msg)
    # blue button is washing hands
    if msg == "blue":
        sink_sound.play()
    # green button is flushing toilet
    elif msg == "green":
        toilet_sound.play()

# connect to mqtt broker
client = mqtt_client.Client(client_id=client_id)
client.connect(broker_ip, broker_port)
client.subscribe(topic, qos=2)
client.on_message = on_message
client.loop_start()

try:
    while True:
        # use time sleep instead of pass to minimize the CPU usage.
        time.sleep(0.1)
except KeyboardInterrupt:
    pygame.quit()
    print("\npygame stopped.")
    client.loop_stop()
    print("mqtt speaker closed.")
