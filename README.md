# Reminder-IoT
This repository stores everything we need to implement our reminder system, which is an AI reminder that supports scalability, muti-modal, real-time inference, dashboard, decomposed subsystems, etc.

## Watch our demo video

[Youtube link](https://youtu.be/yG0fzkwrp3g?si=nT3MOcIuur6gKR5z)

## 1. Folders

* 3D prints: This folder stores the designed 3D printing parts for the hardware.
* dashboard: This folder stores the config file and required packages we need to install when using Nodered.
* data: Data folder is used to store data collected and will be created automatically when running our data collection all-in-one script (utils/all_in_one.py).
* model: Model folder stores everything related to machine learning.
* MQTT: This folder stores the boilerplate code for implementing MQTT communication on various hardware chips.
* sensors: Sensors folder stores everything about the sensors, including hardware info, boilerplate code, et al.
* server: server folder stores a simple Eclipse Mosquitto configuration file.
* utils: This folder stores everything we need to deal with the data: collection, postprocessing, labeling, configuration, et al.

## 2. System Structure
The whole reminder system has three sub-systems: data collection, real-time dashboard, and real-time inference.

![Reminder System Structure](reminder_systems.svg)

* Data Collection sub-system: Data Collection sub-system can be run standalone, as you can see in the figure. It communicates with sensor directly through USB cables, and stores data locally.

* Real-Time Dashboard sub-system: Real-Time Dashboard sub-system mainly relies on three processes: a [mosquitto MQTT broker server](https://mosquitto.org/), mqtt_pub_from_file.py and, a [Nodered instance](https://nodered.org/). It acts like an adds-on, making it not interrupt the data collection process. Basically, it checks the data stream and publishes new data to our MQTT server, then the Nodered will subscribe to all data streams, and display in real-time. Only the mqtt_pub_from_file.py needs to run on the Raspberry Pi, the mosquitto MQTT broker server and Nodered can be run on any computer as long as the computing architecture is supported (x86, arm, et al).

* Real-Time Inference sub-system: Real-Time Inference sub-system works along with the MQTT broker server too, as it needs to subscribe all data and feed the data to do inference. After that, the inference result will be published to the MQTT broker server, making it convenient to display the real-time inference results.

## 3. How to

### 3.1 Data collection

#### 3.1.1 Configurations - Modify `record_config.py`

Before we run our all_in_one.py, let's modify the `record_config.py` according to our environmental layout and hardware.

Step 1. We use USB serial numbers as the unique id to find the specific devices, so we need to make sure they match and there are no errors. Run the helper script `usb_monitor.py` that displays the found USB device with its USB serial number. Then, we plug in one sensor each time and read the USB serial number to verify that it matches the current values, revising it if not. Please follow the description below:

```
  thermal1.csv -> toilet thermal
  tof1.csv -> toilet ToF
  thermal2.csv -> sink thermal
  tof2.csv -> sink ToF
  height1.csv -> the sensor array next to door outside
  height2.csv -> the sensor array next to door inside
``` 

Step 2. Measure the room's layout following the example in lines 40-51. Please do not delete the example code blocks, just comment it out and create a new variable with the same name and measure the required numbers. These numbers will be used for normalization so that our model can adaptively work on different layouts. Please follow the description below:

![Layout Description](restroom_layout-layout_description.drawio.svg)


```
  door_width -> width of door in mm
  door_sensor_height -> the distance between the floor and the bottom of the door sensor in mm
  sink_depth -> the distance between the sensor case and the edge of the counter in mm
  sink_sensor_height -> the distance between the floor and the bottom of the sink sensor in mm
  toilet_depth -> the distance between the sensor case and the furthest point of the toilet in mm
  toilet_sensor_height -> the distance between the floor and the bottom of the toilet sensor in mm
``` 

#### 3.1.2 Run data collection main process - Run `all_in_one.py`

Running all_in_one.py will generate several subprocesses based on your configurations. Once all devices are found, it will enter the case record loop. During the loop it will prompt user to type desired input to lead the record process. Usually, we can define infinite cases. In our case, we just record the start time and the end time, the start time is recorded right after you input the new `subject+number`; the end time is the second event we need and is recorded when you input `e` inside the case session. Just follow the on-screen prompt. The data will be stored in `data` folder with a subfolder named {record date}_{number}. Detailed path will be provided and printed out when you run the script.

### 3.2 Real-time dashboard (Optional)

#### 3.2.1 Install and Configure Mosquitto MQTT broker server
Follow the official instruction to install [mosquitto](https://mosquitto.org/download/). After that, check if the default mosquitto server is running: `ps -ef | grep mosquitto`. You have two ways to run our own mosquitto server with the provided `mosquitto.conf` file (located inside `server` folder):
* Method 1: Stop the default mosquitto server, directly run our mosquitto.conf: `mosquitto -c mosquitto.conf`
* Method 2: Check where it stores mosquitto's default config file, change the content and make it the same with ours. Then, restart the default mosquitto service.

Please note that our mosquitto.conf contains only the necessary config entries. Mosquitto supports more features that would benefit our system and it can be applied in the future.

#### 3.2.2 Install and Configure Node-red

The recommended approach to install Node-red is to install docker through the [instruction](https://nodered.org/docs/getting-started/docker).

Once installed, open the Node-red website through the [instruction](https://nodered.org/docs/getting-started/docker).

To configure the Node-red, we first need to install some needed packges, or another saying: nodes. Follow the [instruction](https://nodered.org/docs/user-guide/editor/palette/manager) to install all nodes listed in `dashboard/installed_packages`.

After that, we need to modify our `dashboard/flows.json` first. Locate line 14 and 15, fill in the correct broker server ip address and port. The port should match your mosquitto.conf, and the server ip address is the one where you run your mosquitto server on.

Then follow the [instruction](https://nodered.org/docs/user-guide/editor/workspace/import-export) to import our dashboard flows: `dashboard/flows.json`. When everything is done, you should be able to find the status of mqtt is green and you can also check your dashboard website though your side panel. Some info can be found [here](https://flows.nodered.org/node/node-red-dashboard).

#### 3.2.3 Configure and Run mqtt_pub_from_file.py

The last thing for real-time dashboard is to run `mqtt_pub_from_file.py` so we can have data streaming to the server and then be distributed to Node-red dashboard.

Before we run it, modify variables (broker_ip, broker_port, folder) accordingly. Then you are good to go. Go back to your dashboard website and refresh the site you should be able to see data streaming in.

### 3.3 Real-time Inference (Optional)

#### 3.3.1 Install and Configure Mosquitto MQTT broker server

Skip this step if you have MQTT running. Otherwise, please refer to 3.2.1 to install and configure the mosquitto mqtt broker server.

#### 3.3.2 Configure and Run mqtt_pub_from_file.py

Skip this step if you have mqtt_pub_from_file.py running. Otherwise, please refer to 3.2.3 to configure and run mqtt_pub_from_file.py.

#### 3.3.3 Configure and Run mqtt_inference_tf.py

Modify variables (broker_ip, broker_port) accordingly. Modify Lines 30, 40, 51, and 62 according to the room layout. This inconvenience will be fixed in the future.

Once all are done, you could just run mqtt_inference_tf.py. Please note that this process can be run on any computer, and we recommend that we run it on a separate node so that different device do their own things.

#### 3.3.4 View Real-time result through Node-red

Now you just need to go back to your dashboard website and refresh the site, you should be able to see inference results.
