# this config file is used to generate works
from data_record import Sensor

# use usb_serial as the unique id to find the specific devices
# device path is no longer supported as it varies when reconnecting

# format:
# "usb_serial": ["filename", Sensor.type]
sensors_info = {
    # "usb_serial": ["filename1", Sensor.tof_single],
    "84:FC:E6:84:3A:2C": ["tof1.csv", Sensor.tof_single],
    "40:4C:CA:F4:EF:58": ["height1.csv", Sensor.tof_penta],
    "EC:DA:3B:BE:6D:80": ["height2.csv", Sensor.tof_penta],
    "64:E8:33:80:91:AC": ["thermal1.csv", Sensor.thermal],
    "64:E8:33:83:F6:C0": ["button1.csv", Sensor.button],
    # hide the following
    # "usb_serial": ["finger1.csv", Sensor.finger],
    # "usb_serial": ["mic1.csv", Sensor.mic],
}

# "usb_serial": ["topic", "client_id", Sensor.type]
sensors_info_mqtt = {
    # "usb_serial": ["topic", "client_id", Sensor.tof_single],
    "84:FC:E6:84:3A:2C": ["test/tof1", "tof1_pi", Sensor.tof_single],
    "40:4C:CA:F4:EF:58": ["test/height1", "height1_pi", Sensor.tof_penta],
    "EC:DA:3B:BE:6D:80": ["test/height2", "height2_pi", Sensor.tof_penta],
    "64:E8:33:80:91:AC": ["test/thermal1", "thermal1_pi", Sensor.thermal],
    # hide the following
    # "usb_serial": ["test/finger1", "finger1_pi", Sensor.finger],
    # "usb_serial": ["test/mic1", "mic1_pi", Sensor.mic],
}
