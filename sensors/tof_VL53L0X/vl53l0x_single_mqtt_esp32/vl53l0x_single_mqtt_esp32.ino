#define DEBUG false  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include "Adafruit_VL53L0X.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
// local info where stores the ssid, password
#include "localinfo.h"

/* Wi-Fi info SSID and PASSWD are two defines stored in localinfo.h,
if you do not have such file, creat one by yourself:
localinfo.h:
--------------------------
#ifndef LOCALINFO_H
#define LOCALINFO_H

#define SSID "your_ssid"
#define PASSWD "password"

#endif
--------------------------
*/
const char* ssid = SSID;
const char* password = PASSWD;

// MQTT broker info
const char* mqtt_server = "192.168.0.101";
const int mqtt_port = 1883;

// MQTT client info
const char* client_node = "tof1_esp32";
const char* pub_topic = "test/tof1";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;

char dataString[8]; //4bytes for each ToF

Adafruit_VL53L0X lox = Adafruit_VL53L0X();

VL53L0X_RangingMeasurementData_t measure;

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  DEBUG_SERIAL.println();
  DEBUG_SERIAL.print("Connecting to ");
  DEBUG_SERIAL.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    DEBUG_SERIAL.print(".");
  }

  DEBUG_SERIAL.println("");
  DEBUG_SERIAL.println("WiFi connected");
  DEBUG_SERIAL.println("IP address: ");
  DEBUG_SERIAL.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    DEBUG_SERIAL.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(client_node)) {
      DEBUG_SERIAL.println("connected");
    } else {
      DEBUG_SERIAL.print("failed, rc=");
      DEBUG_SERIAL.print(client.state());
      DEBUG_SERIAL.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  DEBUG_SERIAL.begin(115200);

  if (!lox.begin()) {
    DEBUG_SERIAL.println(F("Failed to boot VL53L0X"));
    while(1);
  }
  // power 
  DEBUG_SERIAL.println(F("VL53L0X API Simple Ranging example\n\n"));

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 500) {
    lastMsg = now;
    lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
    sprintf(dataString, "%d", measure.RangeMilliMeter);
    DEBUG_SERIAL.println(dataString);

    client.publish(pub_topic, dataString);
  }
}