import pygame
import time
from paho.mqtt import client as mqtt_client


# mqtt info
broker_ip = "172.16.42.101"
broker_port = 1883
topic = "test/finger1_touched"
client_id = "speaker1_pi"

# callback
def on_message(client, userdata, message):
    my_sound.play()
    time.sleep(my_sound.get_length())
    print("played once")

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
except KeyboardInterrupt:
    pygame.quit()
    print("\npygame stopped.")
    client.loop_stop()
    print("mqtt client closed.")