#include "Adafruit_VL53L0X.h"
#define PERIOD 200 //5Hz

Adafruit_VL53L0X lox = Adafruit_VL53L0X();
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);

  lox.begin();

  // wait for 1 second
  delay(1000);

  // start continuous ranging
  lox.startRangeContinuous();
}

void loop() {
  unsigned long nowTime = millis();
  if (nowTime - lastTime > PERIOD) {
    lastTime = nowTime;
    Serial.println(lox.readRange());
  }
}