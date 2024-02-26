#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include <PDM.h>
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
const char* client_node = "mic1_nano";
const char* pub_topic = "test/mic1";

WiFiClient rp2040Client;
PubSubClient client(rp2040Client);

char dataString[8];  // at most 6 bytes to store value int16() (-32768 ~ 32767)

// default number of output channels
static const char channels = 1;

// default PCM output frequency
static const int frequency = 8000;

// Buffer to read samples into, each sample is 16-bits
short sampleBuffer[512];

// Number of audio samples read
volatile int samplesRead;

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

  // DEBUG_SERIAL.println(WiFi.localIP()); // comment out for RP2040/Arduino Nano RP2040 Connect
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

  // Configure the data receive callback
  PDM.onReceive(onPDMdata);

  // Optionally set the gain
  // Defaults to 20 on the BLE Sense and -10 on the Portenta Vision Shields
  PDM.setGain(30);
  
  PDM.setBufferSize(512);

  // Initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate for the Arduino Nano 33 BLE Sense
  // - a 32 kHz or 64 kHz sample rate for the Arduino Portenta Vision Shields
  if (!PDM.begin(channels, frequency)) {
    DEBUG_SERIAL.println("Failed to start PDM!");
    while (1);
  }

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Wait for samples to be read
  if (samplesRead) {

    // Print samples to the serial monitor or plotter
    for (int i = 0; i < samplesRead; i++) {
      sprintf(dataString, "%ld", sampleBuffer[i]);

      DEBUG_SERIAL.println(dataString);
      client.publish(pub_topic, dataString);
    }
    // Clear the read count
    samplesRead = 0;
  }
}

/**
   Callback function to process the data from the PDM microphone.
   NOTE: This callback is executed as part of an ISR.
   Therefore using `Serial` to print messages inside this function isn't supported.
 * */
void onPDMdata() {
  // Query the number of available bytes
  int bytesAvailable = PDM.available();

  // Read into the sample buffer
  PDM.read(sampleBuffer, bytesAvailable);

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}