import time
from file_ops import writeFile
import serial
import serial.tools
import serial.tools.list_ports
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
    def __init__(self, usb_serial=None, filename=None, sensorType=None) -> None:
        self.file = filename
        self.usb_serial = usb_serial
        
        # connect
        self.serial_port = None
        self.ser = None
        self.connect()

        # header
        writeFile(self.file, sensorHeader[sensorType], option="w")

    def run(self):
        print(f"Start recording...{self.file}")
        try:
            while True:
                try:
                    if self.ser.in_waiting:
                        data = self.ser.readline()
                        try:
                            now_time = time.time()
                            data = data.decode("utf-8")[:-2]
                            # print(f"{self.file}\t{data}")
                            writeFile(self.file, f"{now_time},{data}\n", "a")
                        except Exception as e:
                            print("pass one error reading.")
                            pass
                except Exception as e:
                    print(f"ERROR {self.file}:{e}")
                    print("Lost connection, reconnecting...")
                    self.connect()
        except KeyboardInterrupt:
            self.ser.close()
            print(f"\nStopped recording...{self.file}")

    def find_device_by_serial(self):
        while True:
            device_list = serial.tools.list_ports.comports()
            for device in device_list:
                if device.serial_number == self.usb_serial:
                    print(f"Found device {self.file}-{self.usb_serial} on {device.device}")
                    return device.device
            
            print(f"Did not find device: {self.file}-{self.usb_serial}, try again after 5 seconds")
            time.sleep(5)

    def connect(self):
        self.serial_port = self.find_device_by_serial()
        self.ser = serial.Serial(self.serial_port, 115200, timeout=4)
        print(f"Connected {self.serial_port}")


if __name__ == "__main__":
    tof1 = dataRecord("40:4C:CA:F4:EF:58", "sensor_test.csv", Sensor.tof_penta)
    tof1.run()
