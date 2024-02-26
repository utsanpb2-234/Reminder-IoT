#include <Melopero_AMG8833.h>
#define PERIOD 200 // 5Hz

Melopero_AMG8833 sensor;
unsigned long lastTime = 0;
int statusCode = 0;

void setup() {
  Serial.begin(115200);

  // initializing I2C to use default address AMG8833_I2C_ADDRESS_B and Wire (I2C-0):
  Wire.begin();
  sensor.initI2C();

  statusCode = sensor.resetFlagsAndSettings();

  // Serial.print("Setting FPS ... ");
  statusCode = sensor.setFPSMode(FPS_MODE::FPS_10);
}

void loop() {
  unsigned long nowTime = millis();

  if (nowTime - lastTime > PERIOD) {
    lastTime = nowTime;
    
    statusCode = sensor.updateThermistorTemperature();
    statusCode = sensor.updatePixelMatrix();

    for (int x = 0; x < 8; x++){
      for (int y = 0; y < 8; y++){
        Serial.print(sensor.pixelMatrix[y][x]);
        if (y!=7 || x!=7){
          Serial.print(",");
        }
      }
    }
    Serial.println();
  }
}
