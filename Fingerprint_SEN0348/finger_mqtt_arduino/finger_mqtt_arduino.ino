#define DEBUG false  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include <DFRobot_ID809.h>
#define FPSerial Serial1

#include <SPI.h>
#include <WiFiNINA.h>
#include <PubSubClient.h>
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
int status = WL_IDLE_STATUS;     // the WiFi radio's status

// MQTT broker info
const char* mqtt_server = "192.168.0.101";
const int mqtt_port = 1883;

// MQTT client info
const char* client_node = "finger1_nano";
const char* pub_topic = "test/finger1";

WiFiClient rp2040Client;
PubSubClient client(rp2040Client);

DFRobot_ID809 fingerprint;

uint8_t data[6400];  //Full image
char dataString[100];

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  DEBUG_SERIAL.println();
  DEBUG_SERIAL.print("Connecting to ");
  DEBUG_SERIAL.println(ssid);

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    DEBUG_SERIAL.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }
  
  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    DEBUG_SERIAL.print("Attempting to connect to WPA SSID: ");
    DEBUG_SERIAL.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, password);

    // wait 1 second for connection:
    delay(1000);
  }

  DEBUG_SERIAL.println("");
  DEBUG_SERIAL.println("WiFi connected");
  DEBUG_SERIAL.println("IP address: ");

  // Serial.println(WiFi.localIP()); // comment out for RP2040/Arduino Nano RP2040 Connect
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

void setup(){
  /*Init print serial port */
  DEBUG_SERIAL.begin(115200);
  /*Init FPSerial*/
  FPSerial.begin(115200);
  /*Take FPSerial as communication port of fingerprint module */
  fingerprint.begin(FPSerial);
  
  /*Wait for Serial to open*/
  /*Test whether device can communicate properly with mainboard 
    Return true or false
    */
  while(fingerprint.isConnected() == false){
    // Serial.println("Communication with device failed, please check connection");
    /*Get error code information */
    //desc = fingerprint.getErrorDescription();
    //Serial.println(desc);
    delay(1000);
  }

  setup_wifi();
  DEBUG_SERIAL.println("wifi set is done");
  client.setServer(mqtt_server, mqtt_port);
  DEBUG_SERIAL.println("mqtt set is done");
}

void loop(){
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  /*Set the fingerprint module LED ring to blue breathing lighting effect*/
  fingerprint.ctrlLED(/*LEDMode = */fingerprint.eBreathing, /*LEDColor = */fingerprint.eLEDBlue, /*blinkCount = */0);
  // Serial.println("Please release your finger");
  /*Wait for finger to release
    Return 1 when finger is detected, otherwise return 0 
   */
  if (fingerprint.detectFinger()) {
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eFastBlink, /*LEDColor = */fingerprint.eLEDGreen, /*blinkCount = */3);
    //Collect full images
    // fingerprint.getFingerImage(data);
    fingerprint.getQuarterFingerImage(data);

    //Display the image on the screen
    for(uint16_t i = 0; i < 6400 ;){
      sprintf(dataString,"%d,%d,%d,%d,%d,%d,%d,%d",data[i],data[i+1],data[i+2],data[i+3],data[i+4],data[i+5],data[i+6],data[i+7]);
      client.publish(pub_topic, dataString);
      if (!client.connected()) {
        reconnect();
      }
      client.loop();
      i += 8;
    }
    DEBUG_SERIAL.println("sent.");
    client.publish(pub_topic, "end");
  }
  delay(500);
}
