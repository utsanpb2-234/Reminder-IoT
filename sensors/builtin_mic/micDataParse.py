import serial
import time
import numpy as np
import soundfile as sf


ser = serial.Serial("/dev/tty.usbmodem11201", 115200, timeout=4)
sound_file = "test.wav"
sample_rate_hz = 8000

micData = []

try:
    while True:
        if ser.in_waiting:
            data = ser.readline()
            data = data.decode("utf-8")[:-2]
            try:
                data = int(data)
                micData.append(data)
            except:
                print("pass one error reading.")
                pass
except KeyboardInterrupt:
    ser.close()
    print("\nserial closed")
    micData = np.asarray(micData,dtype=np.int16)
    sf.write(sound_file, micData, sample_rate_hz)
    print("sound file saved")