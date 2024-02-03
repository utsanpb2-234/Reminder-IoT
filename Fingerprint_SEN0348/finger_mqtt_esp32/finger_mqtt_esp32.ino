#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include <DFRobot_ID809.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
// local info where stores the ssid, password
#include "localinfo.h"

// Need this for the xiao esp32c3 serial1
#include <HardwareSerial.h>
//Define two Serial devices mapped to the two internal UARTs
HardwareSerial FPSerial(0);

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
const char* client_node = "finger1_esp32";
const char* pub_topic = "test/finger1";

WiFiClient espClient;
PubSubClient client(espClient);

DFRobot_ID809 fingerprint;

uint8_t data[25600];  //Full image
char dataString[8];

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

void setup(){
  /*Init print serial port */
  DEBUG_SERIAL.begin(115200);
  
  /*Init FPSerial on pins TX=6 and RX=7 (-1, -1 means use the default) */
  FPSerial.begin(115200, SERIAL_8N1, -1, -1);

  /*Take FPSerial as communication port of fingerprint module */
  fingerprint.begin(FPSerial);
  
  /*Wait for Serial to open*/
  /*Test whether device can communicate properly with mainboard 
    Return true or false
    */
  while(fingerprint.isConnected() == false){
    DEBUG_SERIAL.println("Communication with device failed, please check connection");
    /*Get error code information */
    //desc = fingerprint.getErrorDescription();
    //Serial.println(desc);
    delay(1000);
  }

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
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
  if (fingerprint.detectFinger()){
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eFastBlink, /*LEDColor = */fingerprint.eLEDGreen, /*blinkCount = */3);
    //Collect full images
    fingerprint.getFingerImage(data);
    for(uint16_t i = 0; i < 25599 ;i++){
      DEBUG_SERIAL.println(data[i]);
    }
    delay(1000);
  }
}