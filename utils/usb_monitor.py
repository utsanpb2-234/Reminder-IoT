# display all USB devices connected to the system in real-time
import serial
import serial.tools
import serial.tools.list_ports
import time
import sys


if __name__ == "__main__":
    try:
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            device_list = serial.tools.list_ports.comports()
            for device in device_list:
                if device.serial_number is not None:
                    print(f"{device.device}: {device.serial_number}, {device.product}")

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nCtrl+c pressed, end program.")
        sys.exit(0)
