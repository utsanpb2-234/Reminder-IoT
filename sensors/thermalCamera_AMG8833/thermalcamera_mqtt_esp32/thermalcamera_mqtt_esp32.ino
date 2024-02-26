#define DEBUG false  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include <Melopero_AMG8833.h>
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
const char* client_node = "thermal1_esp32";
const char* pub_topic = "test/thermal1";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;

#define buffersize 512 //64 data, each data cost at most 5 bytes(0-255), with one additional separtor.
char dataString[buffersize];

Melopero_AMG8833 sensor;

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

  // initializing I2C to use default address AMG8833_I2C_ADDRESS_B and Wire (I2C-0):
  Wire.begin();
  sensor.initI2C();

  // DEBUG_SERIAL.print("Resetting sensor ... ");  
  int statusCode = sensor.resetFlagsAndSettings();
  DEBUG_SERIAL.println(sensor.getErrorDescription(statusCode));

  // DEBUG_SERIAL.print("Setting FPS ... ");
  statusCode = sensor.setFPSMode(FPS_MODE::FPS_10);
  DEBUG_SERIAL.println(sensor.getErrorDescription(statusCode));

  setup_wifi();
  client.setBufferSize(buffersize); //increase the buffer size to make sure the 300byte-long dataString can be sent
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
    int statusCode = sensor.updateThermistorTemperature();
    statusCode = sensor.updatePixelMatrix();
    String data = "";
    for (int x = 0; x < 8; x++){
      for (int y = 0; y < 8; y++){
        data += String(sensor.pixelMatrix[y][x]);
        if (y!=7 || x!=7){
          data += ",";
        }
      }
    }
    data.toCharArray(dataString, buffersize);
    DEBUG_SERIAL.println(dataString);
    client.publish(pub_topic, dataString);
  }
}