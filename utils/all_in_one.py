from threading import Thread
from case_record import caseRecord
from data_record import dataRecord, Sensor
import time


if __name__ == "__main__":
    case1 = caseRecord("case1.csv")
    tof1 = dataRecord("/dev/cu.usbmodem11101", "tof1.csv", Sensor.tof_single)

    tof1_thread = Thread(target=tof1.run, daemon=True)

    tof1_thread.start()

    case1.run()

    time.sleep(2)
