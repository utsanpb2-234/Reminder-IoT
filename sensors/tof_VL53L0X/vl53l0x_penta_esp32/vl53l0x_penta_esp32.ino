#include <Adafruit_VL53L0X.h>
#define PERIOD 200 //5Hz

unsigned long lastTime = 0;
char msgStr[50];
uint16_t data[5];

/*
reset pins connection - xiao esp32c3
sensor 1: D0
sensor 2: D1
sensor 3: D2
sensor 4: D3
sensor 5: D10
*/

// address we will assign if dual sensor is present
#define LOX1_ADDRESS 0x30
#define LOX2_ADDRESS 0x31
#define LOX3_ADDRESS 0x32
#define LOX4_ADDRESS 0x33
#define LOX5_ADDRESS 0x34

// set the pins to shutdown
#define SHT_LOX1 D0
#define SHT_LOX2 D1
#define SHT_LOX3 D2
#define SHT_LOX4 D3
#define SHT_LOX5 D10

// objects for the vl53l0x
Adafruit_VL53L0X lox1 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox2 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox3 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox4 = Adafruit_VL53L0X();
Adafruit_VL53L0X lox5 = Adafruit_VL53L0X();

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
  lox1.startRangeContinuous();
  lox2.startRangeContinuous();
  lox3.startRangeContinuous();
  lox4.startRangeContinuous();
  lox5.startRangeContinuous();
}

void read_penta_sensors() {
  data[0] = lox1.readRange();
  data[1] = lox2.readRange();
  data[2] = lox3.readRange();
  data[3] = lox4.readRange();
  data[4] = lox5.readRange();

  sprintf(msgStr, "%d,%d,%d,%d,%d", data[0],data[1],data[2],data[3],data[4]);
  Serial.println(msgStr);
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
  unsigned long nowTime = millis();

  if (nowTime - lastTime > PERIOD) {
    lastTime = nowTime;
    read_penta_sensors();
  }
}