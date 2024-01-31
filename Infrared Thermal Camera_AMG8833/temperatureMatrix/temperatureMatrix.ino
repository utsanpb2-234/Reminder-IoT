#include <Melopero_AMG8833.h>

Melopero_AMG8833 sensor;

void setup() {
  Serial.begin(115200);

  // initializing I2C to use default address AMG8833_I2C_ADDRESS_B and Wire (I2C-0):
  Wire.begin();
  sensor.initI2C();

  // Serial.print("Resetting sensor ... ");  
  int statusCode = sensor.resetFlagsAndSettings();
  Serial.println(sensor.getErrorDescription(statusCode));

  // Serial.print("Setting FPS ... ");
  statusCode = sensor.setFPSMode(FPS_MODE::FPS_10);
  Serial.println(sensor.getErrorDescription(statusCode));
}

void loop() {
  // Serial.print("Updating thermistor temperature ... ");
  int statusCode = sensor.updateThermistorTemperature();
  // Serial.println(sensor.getErrorDescription(statusCode));

  // Serial.print("Updating pixel matrix ... ");
  statusCode = sensor.updatePixelMatrix();
  // Serial.println(sensor.getErrorDescription(statusCode));

  // Serial.print("Thermistor temp: ");
  // Serial.print(sensor.thermistorTemperature);
  // Serial.println("°C");

  // Serial.println("Temperature Matrix: ");
  for (int x = 0; x < 8; x++){
    for (int y = 0; y < 8; y++){
      Serial.print(sensor.pixelMatrix[y][x]);
      if (y!=7 || x!=7){
        Serial.print(",");
      }
    }
    // Serial.println();
  }
  Serial.println();

  delay(100);
}
