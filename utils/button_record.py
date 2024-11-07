# deprecated since we dont use pi to monitor the buttons
import time
from file_ops import writeFile
from gpiozero import LED, Button


class buttonRecord():
    def __init__(self, button_pin=None, led_pin=None, label=None, is_running=True, filename=None) -> None:
        self.button_pin = button_pin
        self.led_pin = led_pin
        self.label = label
        self.is_running = is_running
        self.file = filename
        
        # initialize
        self.button = Button(self.button_pin)
        self.led = LED(self.led_pin)

        # header
        writeFile(self.file, "time,activity\n", option="w")

    def run(self):
        while self.is_running:
            if self.button.is_pressed:
                self.led.on()
                print(f"{self.label}", end=",")
                writeFile(self.file, f"{time.time()},{self.label}\n", "a")
                time.sleep(0.4)
                self.led.off()
