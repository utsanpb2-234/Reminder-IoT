#include <AceButton.h>
using namespace ace_button;

#define BLUE_LED D1
#define BLUE_BUTTON D2
#define GREEN_LED D0
#define GREEN_BUTTON D10

AceButton blue_btn(BLUE_BUTTON);
AceButton green_btn(GREEN_BUTTON);

const int LED_ON = HIGH;
const int LED_OFF = LOW;

void handleEvent(AceButton*, uint8_t, uint8_t);

void setup() {
  Serial.begin(115200);
  
  // set LED pins output
  pinMode(BLUE_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  // initialize LEDs to low
  digitalWrite(BLUE_LED, LED_OFF);
  digitalWrite(GREEN_LED, LED_OFF);

  // Button uses the built-in pull up register.
  pinMode(BLUE_BUTTON, INPUT_PULLUP);
  pinMode(GREEN_BUTTON, INPUT_PULLUP);

  // button configuration
  ButtonConfig* buttonConfig = ButtonConfig::getSystemButtonConfig();
  buttonConfig->setEventHandler(handleEvent);
  buttonConfig->setFeature(ButtonConfig::kFeatureClick);
  buttonConfig->setFeature(ButtonConfig::kFeatureDoubleClick);
  buttonConfig->setFeature(ButtonConfig::kFeatureLongPress);
  buttonConfig->setFeature(ButtonConfig::kFeatureRepeatPress);
}

void loop() {
  blue_btn.check();
  green_btn.check();
}

void handleEvent(AceButton* button, uint8_t eventType, uint8_t buttonState) {

  // // Print out a message for all events.
  // Serial.print(F("handleEvent(): pin: "));
  // Serial.print(button->getPin());
  // Serial.print(F("; eventType: "));
  // Serial.print(AceButton::eventName(eventType));
  // Serial.print(F("; buttonState: "));
  // Serial.println(buttonState);

  // Control the LED only for the Pressed and Released events.
  // Notice that if the MCU is rebooted while the button is pressed down, no
  // event is triggered and the LED remains off.
  switch (eventType) {
    case AceButton::kEventPressed:
      if (button->getPin() == BLUE_BUTTON) {
        digitalWrite(BLUE_LED, LED_ON);
        Serial.println("blue");
      }
      else if (button->getPin() == GREEN_BUTTON) {
        digitalWrite(GREEN_LED, LED_ON);
        Serial.println("green");
      }
      break;
    case AceButton::kEventReleased:
      digitalWrite(BLUE_LED, LED_OFF);
      digitalWrite(GREEN_LED, LED_OFF);
      break;
  }
}
