/*********
  MQTT publish example for arduino
*********/

#include <WiFiNINA.h>
#include <SPI.h>
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
const char* client_node = "arduinosample";
const char* pub_topic = "test/topic";

WiFiClient rp2040Client;
PubSubClient client(rp2040Client);
long lastMsg = 0;
float data = 1.0;

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(client_node)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    data += 1.0;
    char dataString[8];
    dtostrf(data, 1, 2, dataString);
    Serial.print("Data: ");
    Serial.println(dataString);
    client.publish(pub_topic, dataString);
  }
}