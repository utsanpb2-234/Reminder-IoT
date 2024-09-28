from threading import Thread
from multiprocessing import Process
from case_record import caseRecord
from data_record import dataRecord, Sensor
from button_record import buttonRecord
import time
from record_config import sensors_info, button_info
import datetime
import os


if __name__ == "__main__":
    date_cur = datetime.datetime.now().strftime("%Y%m%d")
    is_running = True
    record_idx = 0
    folder = f"{date_cur}_{record_idx}"
    while os.path.exists(folder):
        record_idx += 1
        folder = f"{date_cur}_{record_idx}"

    os.makedirs(folder)

    for sensor_port in sensors_info.keys():
        sensor = dataRecord(sensor_port, f"{folder}/{sensors_info[sensor_port][0]}", sensors_info[sensor_port][1])
        sensor_thread = Process(target=sensor.run, args=(), daemon=True)
        sensor_thread.start()
        time.sleep(1)
    
    for label in button_info.keys():
        button = Thread(target=buttonRecord, args=(button_info[label][0], button_info[label][0], label,), daemon=True)
        button.start()
        time.sleep(0.5)
    
    case1 = caseRecord(f"{folder}/case1.csv")
    case1.run()

    time.sleep(2)
