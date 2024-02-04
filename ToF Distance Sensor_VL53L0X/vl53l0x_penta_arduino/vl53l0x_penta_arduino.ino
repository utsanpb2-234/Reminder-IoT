#include <Adafruit_VL53L0X.h>

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
    Serial.println(F("Failed to boot 1st VL53L0X"));
    while(1);
  }
  delay(10);

  // activating LOX2
  digitalWrite(SHT_LOX2, HIGH);
  delay(10);

  //initing LOX2
  if(!lox2.begin(LOX2_ADDRESS)) {
    Serial.println(F("Failed to boot 2nd VL53L0X"));
    while(1);
  }

  // activating LOX3
  digitalWrite(SHT_LOX3, HIGH);
  delay(10);

  //initing LOX3
  if(!lox3.begin(LOX3_ADDRESS)) {
    Serial.println(F("Failed to boot 3rd VL53L0X"));
    while(1);
  }

  // activating LOX4
  digitalWrite(SHT_LOX4, HIGH);
  delay(10);

  //initing LOX4
  if(!lox4.begin(LOX4_ADDRESS)) {
    Serial.println(F("Failed to boot 4th VL53L0X"));
    while(1);
  }

  // activating LOX5
  digitalWrite(SHT_LOX5, HIGH);
  delay(10);

  //initing LOX5
  if(!lox5.begin(LOX5_ADDRESS)) {
    Serial.println(F("Failed to boot 5th VL53L0X"));
    while(1);
  }
}

void read_dual_sensors() {
  
  lox1.rangingTest(&measure1, false); // pass in 'true' to get debug data printout!
  lox2.rangingTest(&measure2, false); // pass in 'true' to get debug data printout!
  lox3.rangingTest(&measure3, false); // pass in 'true' to get debug data printout!
  lox4.rangingTest(&measure4, false); // pass in 'true' to get debug data printout!
  lox5.rangingTest(&measure5, false); // pass in 'true' to get debug data printout!

  // print readings
  if(measure1.RangeStatus != 4) {     // if not out of range
    if (measure1.RangeMilliMeter > 50){
      Serial.print("|");
    }
    else {
      Serial.print("T");
    }
  }
  else {
    Serial.print("|");
  }

  if(measure2.RangeStatus != 4) {     // if not out of range
    if (measure2.RangeMilliMeter > 50){
      Serial.print("|");
    }
    else {
      Serial.print("T");
    }
  }
  else {
    Serial.print("|");
  }

  if(measure3.RangeStatus != 4) {     // if not out of range
    if (measure3.RangeMilliMeter > 50){
      Serial.print("|");
    }
    else {
      Serial.print("T");
    }
  }
  else {
    Serial.print("|");
  }

  if(measure4.RangeStatus != 4) {     // if not out of range
    if (measure4.RangeMilliMeter > 50){
      Serial.print("|");
    }
    else {
      Serial.print("T");
    }
  }
  else {
    Serial.print("|");
  }

  if(measure5.RangeStatus != 4) {     // if not out of range
    if (measure5.RangeMilliMeter > 50){
      Serial.print("|");
    }
    else {
      Serial.print("T");
    }
  }
  else {
    Serial.print("|");
  }
  
  Serial.println();
}

void setup() {
  Serial.begin(115200);

  // wait until serial port opens for native USB devices
  while (! Serial) { delay(1); }

  pinMode(SHT_LOX1, OUTPUT);
  pinMode(SHT_LOX2, OUTPUT);
  pinMode(SHT_LOX3, OUTPUT);
  pinMode(SHT_LOX4, OUTPUT);
  pinMode(SHT_LOX5, OUTPUT);

  Serial.println(F("Shutdown pins inited..."));

  digitalWrite(SHT_LOX1, LOW);
  digitalWrite(SHT_LOX2, LOW);
  digitalWrite(SHT_LOX3, LOW);
  digitalWrite(SHT_LOX4, LOW);
  digitalWrite(SHT_LOX5, LOW);

  Serial.println(F("Sensors are in reset mode...(pins are low)"));
  
  Serial.println(F("Starting..."));
  setID();
}

void loop() {
   
  read_dual_sensors();
  delay(100);
}
