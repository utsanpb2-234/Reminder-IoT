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

# "port": ["topic", "client_id", Sensor.type]
sensors_info_mqtt = {
    # "port1": ["topic", "client_id", Sensor.tof_single],
    "/dev/ttyACM0": ["test/tof1", "tof1_pi", Sensor.tof_single],
    "/dev/ttyACM1": ["test/tof2", "tof2_pi", Sensor.tof_single],
    "/dev/ttyACM2": ["test/height1", "height1_pi", Sensor.tof_penta],
    "/dev/ttyACM3": ["test/thermal1", "thermal1_pi", Sensor.thermal],
    "/dev/ttyACM4": ["test/finger1", "finger1_pi", Sensor.finger],
    "/dev/ttyACM5": ["test/mic1", "mic1_pi", Sensor.mic],
}