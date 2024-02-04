/*!
 *@file getQuarterFingerImage.ino
 *@brief Store the collected fingerprint image in the SD card and display it on the screen, can select to obtain quarter image or full image
 *This example needs to be used with screen, SD card，and high-performance main controllers. 
 *@copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
 *@licence     The MIT License (MIT)
 *@author [fengli](li.feng@dfrobot.com)
 *@version  V1.0
 *@date  2021-6-01
 *@get from https://www.dfrobot.com
 *@https://github.com/DFRobot/DFRobot_ID809
*/
#include <DFRobot_ID809.h>
#define FPSerial Serial1

DFRobot_ID809 fingerprint;

uint8_t data[25600];  //Full image


void setup(){
  /*Init print serial port */
  Serial.begin(115200);
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
}

void loop(){
  /*Set the fingerprint module LED ring to blue breathing lighting effect*/
  fingerprint.ctrlLED(/*LEDMode = */fingerprint.eBreathing, /*LEDColor = */fingerprint.eLEDBlue, /*blinkCount = */0);
  // Serial.println("Please release your finger");
  /*Wait for finger to release
    Return 1 when finger is detected, otherwise return 0 
   */
  if (fingerprint.detectFinger()) {
    fingerprint.ctrlLED(/*LEDMode = */fingerprint.eFastBlink, /*LEDColor = */fingerprint.eLEDGreen, /*blinkCount = */3);
    //Collect full images
    fingerprint.getFingerImage(data);

    //Display the image on the screen
    for(uint16_t i = 0; i < 25599 ;i++){
      Serial.print(data[i]);
      Serial.print(",");
    }
    Serial.println(data[25599]);
  }
  delay(500);
}
