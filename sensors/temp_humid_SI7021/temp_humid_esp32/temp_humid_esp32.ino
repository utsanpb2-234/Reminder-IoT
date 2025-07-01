#include <Adafruit_Si7021.h>
#define PERIOD 200 //5Hz
#define PIR_PIN D0 //PIR pin

Adafruit_Si7021 humid_sensor = Adafruit_Si7021();
float humid_value;
float temp_value;
int PIR_value;

char dataString[20];
unsigned long lastTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  humid_sensor.begin();
}

void loop() {
  unsigned long nowTime = millis();
  if (nowTime - lastTime > PERIOD) {
    lastTime = nowTime;
    humid_value = humid_sensor.readHumidity();
    temp_value = humid_sensor.readTemperature();
    PIR_value = analogRead(PIR_PIN);

    sprintf(dataString, "%.3f,%.3f,%d", humid_value, temp_value,PIR_value);
    Serial.println(dataString);
  }
}