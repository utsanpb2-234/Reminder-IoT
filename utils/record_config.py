# this config file is used to generate works
from data_record import Sensor

# format:
# "port": ["filename", Sensor.type]
sensors_info = {
    # "port1": ["filename1", Sensor.tof_single],
    "/dev/ttyACM0": ["tof1.csv", Sensor.tof_single],
    "/dev/ttyACM1": ["tof2.csv", Sensor.tof_single],
    "/dev/ttyACM2": ["height1.csv", Sensor.tof_penta],
    "/dev/ttyACM3": ["thermal1.csv", Sensor.thermal],
    "/dev/ttyACM4": ["finger1.csv", Sensor.finger],
    "/dev/ttyACM5": ["mic1.csv", Sensor.mic],
}