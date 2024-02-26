import pygame
import time
from paho.mqtt import client as mqtt_client
import datetime
import logging
import logging.config

logging.config.fileConfig(fname='logging_config.ini', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

# mqtt info
broker_ip = "192.168.0.101"
broker_port = 1883
topic = "test/finger1"
client_id = "speaker1_pi"

# callback
def on_message(client, userdata, message):
    #time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.debug("start playing once.")
    my_sound.play()
    time.sleep(my_sound.get_length())

# connect to mqtt broker
client = mqtt_client.Client(client_id)
client.connect(broker_ip, broker_port)
client.subscribe(topic, qos=2)
client.on_message = on_message
client.loop_start()

# pygame initialization
pygame.init()

sample_file = "audio_file.wav"
my_sound = pygame.mixer.Sound(sample_file)

try:
    while True:
        # use time sleep instead of pass to minimize the CPU usage.
        time.sleep(5)
        logger.info("slept 5 seconds")
except KeyboardInterrupt:
    pygame.quit()
    print("\npygame stopped.")
    client.loop_stop()
    print("mqtt client closed.")
