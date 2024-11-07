import sounddevice as sd
import soundfile as sf
import numpy
import queue
import sys
from scipy.io.wavfile import write
import time
from multiprocessing import Process
from threading import Thread


class soundDeviceRecord():
    def __init__(self, usb_name=None, filename=None, fs=44100) -> None:
        self.file = filename.split(".")[0]
        self.usb_name = usb_name
        self.fs = fs
        
        # connect
        self.usb_id = self.find_device_by_name()
    
    def run(self):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        print(f"Start recording...{self.file}")
        filename = f"{self.file}_{time.time()}.wav"
        with sf.SoundFile(filename, mode='x', samplerate=self.fs, channels=1) as file:
            with sd.InputStream(samplerate=self.fs, device=self.usb_id, channels=1, callback=callback, dtype="float32"):
                while True:
                    file.write(q.get())

        print(f"Finished recording {self.file}.")

    def find_device_by_name(self):
        while True:
            device_list = sd.query_devices()
            for device in device_list:
                if self.usb_name in device["name"]:
                    print(f"Found device {self.file}-{self.usb_name} with index: {device['index']}")
                    return device["index"]
            
            print(f"Did not find device: {self.file}-{self.usb_name}, try again after 5 seconds")
            time.sleep(5)


if __name__ == "__main__":
    sound1 = soundDeviceRecord(usb_name="USB PnP Sound Device", filename="test_sound1.wav")
    sound1.run()
    