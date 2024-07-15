import time
from file_ops import writeFile
import serial
from enum import Enum


class Sensor(Enum):
    tof_single = 1
    thermal = 2
    finger = 3
    mic = 4
    tof_penta = 5


sensorHeader = {
    Sensor.tof_single: "time,tof\n",
    Sensor.thermal: "time" + "".join([f",thermal{i}" for i in range(64)]) + "\n",
    Sensor.finger: "time" + "".join([f",finger{i}" for i in range(6400)]) + "\n",
    Sensor.mic: "time,mic\n",
    Sensor.tof_penta: "time" + "".join([f",tof{i}" for i in range(5)]) + "\n",
}


class dataRecord():
    def __init__(self, port=None, filename=None, sensorType=None) -> None:
        self.file = filename
        self.port = port

        # open serial port
        self.ser = serial.Serial(self.port, 115200, timeout=4)

        # header
        writeFile(self.file, sensorHeader[sensorType], option="w")

    def run(self):
        print(f"start recording...{self.file}")
        try:
            while True:
                if self.ser.in_waiting:
                    data = self.ser.readline()
                    try:
                        now_time = time.time()
                        data = data.decode("utf-8")[:-2]
                        writeFile(self.file, f"{now_time},{data}\n", "a")
                    except:
                        print("pass one error reading.")
                        pass
        except KeyboardInterrupt:
            self.ser.close()
            print(f"stopped recording...{self.file}")


if __name__ == "__main__":
    tof1 = dataRecord("/dev/cu.usbmodem11101", "test.csv", Sensor.tof_single)
    tof1.run()
