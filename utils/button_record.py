import time
from file_ops import writeFile
from gpiozero import LED, Button


def buttonRecord(button_pin, led_pin, label):
    button = Button(button_pin)
    led = LED(led_pin)
    global is_running

    while is_running:
        if button.is_pressed:
            led.on()
            print(f"{time.time()}: {label} button is pressed")
            time.sleep(0.4)
            led.off()
