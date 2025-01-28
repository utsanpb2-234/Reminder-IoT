# Reminder-IoT
This repository stores everything we need to implement our reminder system, which is an AI reminder that supports scalability, muti-modal, real-time inference, dashboard, decomposed subsystems, etc.

## 1. Folders

* 3D prints: This folder stores the designed 3D printing parts for the hardware.
* dashboard: This folder stores the config file and required packages we need to install when using Nodered.
* data: Data folder is used to store data collected and will be created automatically when running our data collection all-in-one script (utils/all_in_one.py).
* model: Model folder stores everything related to machine learning.
* MQTT: This folder stores the boilerplate code for implementating MQTT communication on various hardware chips.
* sensors: Sensors folder stores everything about the sensors, including hardware info, boilerplate code, et al.
* server: server folder stores a simple Eclipse Mosquitto configuration file.
* utils: This folder stores everything we need to deal with the data: collection, postprocessing, labeling, configuration, et al.

## 2. System Structure
The whole reminder system has three sub-systems: data collection, real-time dashboard, and real-time inference.

![Reminder System Structure](reminder_systems.svg)

* Data Collection sub-system: Data Collection sub-system can be run standalone, as you can see in the figure. It communicates with sensor directly through USB cables, and stores data locally.

* Real-Time Dashboard sub-system: Real-Time Dashboard sub-system mainly relies on three processes: a [mosquitto MQTT broker server](https://mosquitto.org/), mqtt_pub_from_file.py and, a [Nodered instance](https://nodered.org/). It acts like an adds-on, making it not interrupt the data collection process. Basicly, it checks the data stream and publish new data to our MQTT server, then the Nodered will subscribe all data stream, and display in real-time. Only the mqtt_pub_from_file.py needs to run on the Raspberry Pi, the mosquitto MQTT broker server and Nodered can be run on any computer as long as the computing architecture is supported (x86, arm, et al).

* Real-Time Inference sub-system: Real-Time Inference sub-system works along with the MQTT broker server too, as it needs to subscribe all data and feeds the data to do inference. After that, the inference result will be published to the MQTT broker server, making it convenient to display the real-time inference results.

## 3. How to

### 3.1 Data collection

### 3.2 Real-time dashboard

### 3.3 Real-time Inference
