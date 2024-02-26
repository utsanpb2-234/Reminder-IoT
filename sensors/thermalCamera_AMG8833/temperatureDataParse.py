import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import interpolate

ser = serial.Serial("/dev/tty.usbmodem11101", 9600, timeout=4)

fig, ax = plt.subplots(nrows=1, figsize=(5,5), sharex=True)

temperaturedata = np.zeros((8,8))
x_old = np.arange(1,9,1)
y_old = np.arange(1,9,1)
x_new = np.arange(1,9,0.33)
y_new = np.arange(1,9,0.33)

xgrid = np.arange(25)
ygrid = np.arange(25)

def animate(i,):
    if ser.in_waiting:
        data = ser.readline()
        data = data.decode("utf-8")[:-2]
        data = data.split(",")
        data = [float(i) for i in data]
        global temperaturedata
        temperaturedata = np.reshape(data, (8, 8))
        print(temperaturedata)
        f = interpolate.interp2d(x_old, y_old, temperaturedata, kind='linear')
        temperaturedata = f(x_new, y_new)
    
    ax.pcolormesh(xgrid, ygrid, temperaturedata, vmin=18, vmax=35)
    ax.set_frame_on(False)

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()