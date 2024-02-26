import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

width = 80
height = 80
ser = serial.Serial("/dev/tty.usbmodem11201", 115200, timeout=4)

fig, ax = plt.subplots(nrows=1, figsize=(5,5), sharex=True)

fingerdata = np.zeros((width,height))

def animate(i,):
    if ser.in_waiting:
        data = ser.readline()
        data = data.decode("utf-8")[:-2]
        data = data.split(",")
        data = [int(i) for i in data]
        global fingerdata
        fingerdata = np.reshape(data, (width, height))
        print(fingerdata)
    
    ax.imshow(fingerdata)

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()