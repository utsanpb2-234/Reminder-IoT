from threading import Thread
from case_record import caseRecord
from data_record import dataRecord, Sensor
import time
from record_config import *


if __name__ == "__main__":

    for sensor_port in sensors_info.keys():
        sensor = dataRecord(sensor_port, sensors_info[sensor_port][0], sensors_info[sensor_port][1])
        sensor_thread = Thread(target=sensor.run, daemon=True)
        sensor_thread.start()

    case1 = caseRecord("case1.csv")
    case1.run()

    time.sleep(2)
