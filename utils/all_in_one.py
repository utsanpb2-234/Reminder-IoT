# main function to run to collect data and record case
# it runs all the processes in parallel
from threading import Thread
from multiprocessing import Process
from case_record import caseRecord
from data_record import dataRecord, Sensor
from sound_record import soundDeviceRecord
import time
from record_config import sensors_info
import datetime
import os


def sensor_worker(usb_serial, filename, sensor_type):
    sensor = dataRecord(usb_serial, filename, sensor_type)
    sensor.run()

def sound_worker(usb_name, filename):
    sound_instance = soundDeviceRecord(usb_name=usb_name, filename=filename)
    sound_instance.run()

if __name__ == "__main__":
    
    # data root dir
    file_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(parent_dir, "data")

    # prepare data root folder
    date_cur = datetime.datetime.now().strftime("%Y%m%d")
    record_idx = 0
    folder = f"{data_dir}/{date_cur}_{record_idx}"
    while os.path.exists(folder):
        record_idx += 1
        folder = f"{data_dir}/{date_cur}_{record_idx}"

    os.makedirs(folder)

    # start sensor process
    for sensor_port in sensors_info.keys():
        sensor_process = Process(target=sensor_worker, args=(sensor_port, f"{folder}/{sensors_info[sensor_port][0]}", sensors_info[sensor_port][1]), daemon=True)
        sensor_process.start()
        time.sleep(1)

    # start sound record process
    sound_process = Process(target=sound_worker, args=("USB PnP Sound Device", f"{folder}/sound1.wav"))
    sound_process.start()
    time.sleep(2)

    print(f"Data is stored at {folder}\n")

    case1 = caseRecord(f"{folder}/case1.csv")
    case1.run()
    
    time.sleep(2)
    
    sound_process.terminate()
    print("all processes are ended.")
