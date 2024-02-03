#define DEBUG false  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#include <Adafruit_VL53L0X.h>
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
const char* client_node = "height1_nano";
const char* pub_topic = "test/height1";

WiFiClient rp2040Client;
PubSubClient client(rp2040Client);
long lastMsg = 0;

char dataString[30]; //4bytes for each ToF, 5 ToF in total, plus some spaces for separators

/*
reset pins connection - arduino nano rp2040 connect
sensor 1: D9 (GPIO21)
sensor 2: D8 (GPIO20)
sensor 3: D7 (GPIO19)
sensor 4: D6 (GPIO18)
sensor 5: D5 (GPIO17)
*/

// address we will assign if dual sensor is present
#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31
#define LOX3_ADDRESS 0x32
#define LOX4_ADDRESS 0x33
#define LOX5_ADDRESS 0x34

// set the pins to shutdown
#define SHT_LOX1 21
#define SHT_LOX2 20
#define SHT_LOX3 19
#define SHT_LOX4 18
#define SHT_LOX5 17

// objects for the vl53l0x
Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox3 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox4 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox5 = Adafruit_VL53L0X();

// this holds the measurement
VL53L0X_RangingMeasurementData_t measure1;
VL53L0X_RangingMeasurementData_t measure2;
VL53L0X_RangingMeasurementData_t measure3;
VL53L0X_RangingMeasurementData_t measure4;
VL53L0X_RangingMeasurementData_t measure5;

/*
    Reset all sensors by setting all of their XSHUT pins low for delay(10), then set all XSHUT high to bring out of reset
    Keep sensor #1 awake by keeping XSHUT pin high
    Put all other sensors into shutdown by pulling XSHUT pins low
    Initialize sensor #1 with lox.begin(new_i2c_address) Pick any number but 0x29 and it must be under 0x7F. Going with 0x30 to 0x3F is probably OK.
    Keep sensor #1 awake, and now bring sensor #2 out of reset by setting its XSHUT pin high.
    Initialize sensor #2 with lox.begin(new_i2c_address) Pick any number but 0x29 and whatever you set the first sensor to
 */
void setID() {
  // all reset
  digitalWrite(SHT_LOX1, LOW);    
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  digitalWrite(SHT_LOX5, LOW);
  delay(10);

  // all unreset
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, HIGH);
  digitalWrite(SHT_LOX3, HIGH);
  digitalWrite(SHT_LOX4, HIGH);
  digitalWrite(SHT_LOX5, HIGH);
  delay(10);

  // activating LOX1 and resetting all others
  digitalWrite(SHT_LOX1, HIGH);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  digitalWrite(SHT_LOX5, LOW);

  // initing LOX1
  if(!lox1.begin(LOX1_ADDRESS)) {
    DEBUG_SERIAL.println(F("Failed to boot 1st VL53L0X"));
    while(1);
  }
  delay(10);

  // activating LOX2
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  //initing LOX2
  if(!lox2.begin(LOX2_ADDRESS)) {
    DEBUG_SERIAL.println(F("Failed to boot 2nd VL53L0X"));
    while(1);
  }

  // activating LOX3
  digitalWrite(SHT_LOX3, HIGH);
  delay(10);

  //initing LOX3
  if(!lox3.begin(LOX3_ADDRESS)) {
    DEBUG_SERIAL.println(F("Failed to boot 3rd VL53L0X"));
    while(1);
  }

  // activating LOX4
  digitalWrite(SHT_LOX4, HIGH);
  delay(10);

  //initing LOX4
  if(!lox4.begin(LOX4_ADDRESS)) {
    DEBUG_SERIAL.println(F("Failed to boot 4th VL53L0X"));
    while(1);
  }

  // activating LOX5
  digitalWrite(SHT_LOX5, HIGH);
  delay(10);

  //initing LOX5
  if(!lox5.begin(LOX5_ADDRESS)) {
    DEBUG_SERIAL.println(F("Failed to boot 5th VL53L0X"));
    while(1);
  }
}

void read_dual_sensors() {
  
  lox1.rangingTest(&measure1, false); // pass in 'true' to get debug data printout!
  lox2.rangingTest(&measure2, false); // pass in 'true' to get debug data printout!
  lox3.rangingTest(&measure3, false); // pass in 'true' to get debug data printout!
  lox4.rangingTest(&measure4, false); // pass in 'true' to get debug data printout!
  lox5.rangingTest(&measure5, false); // pass in 'true' to get debug data printout!
  
  sprintf(dataString, "%d,%d,%d,%d,%d", measure1.RangeMilliMeter, measure2.RangeMilliMeter, measure3.RangeMilliMeter, measure4.RangeMilliMeter, measure5.RangeMilliMeter);
  DEBUG_SERIAL.println(dataString);

  client.publish(pub_topic, dataString);
  
}

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

  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);
  pinMode(SHT_LOX3, OUTPUT);
  pinMode(SHT_LOX4, OUTPUT);
  pinMode(SHT_LOX5, OUTPUT);

  DEBUG_SERIAL.println(F("Shutdown pins inited..."));

  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  digitalWrite(SHT_LOX5, LOW);

  DEBUG_SERIAL.println(F("Sensors are in reset mode...(pins are low)"));
  
  DEBUG_SERIAL.println(F("Starting..."));
  setID();

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
    read_dual_sensors();
  }
}