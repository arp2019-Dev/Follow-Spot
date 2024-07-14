#include <Arduino.h>

#include <AccelStepper.h>

// Pinouts
const int stepPinX = 2;
const int dirPinX = 3;
const int stepPinY = 6;
const int dirPinY = 7;
const int lightPin = 8;
const int lightTrigger = 9;
bool lightState = false;

// Motor Initialization
AccelStepper stepperX(1, stepPinX, dirPinX);
AccelStepper stepperY(1, stepPinY, dirPinY);

// Variables to track desired positions
long desiredPositionX = 0;
long desiredPositionY = 0;

void setup() {
  Serial.begin(9600);
  
  // Motor X setup
  stepperX.setMaxSpeed(1000); 
  stepperX.setAcceleration(500); 

  // Motor Y setup
  stepperY.setMaxSpeed(1000); 
  stepperY.setAcceleration(500); 
  
  pinMode(lightTrigger, INPUT_PULLUP);
  pinMode(lightPin, OUTPUT);
  
  lightState = false; // Turn light off on startup
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    int commaIndex = command.indexOf(',');
    if (commaIndex > 0) {
      int stepsX = command.substring(0, commaIndex).toInt();
      int stepsY = command.substring(commaIndex + 1).toInt();

      // Invert directions
      stepsX = -stepsX;
      stepsY = -stepsY;

      desiredPositionX += stepsX;
      desiredPositionY += stepsY;
    }
  }
  
  // Set the target position for smoother movement
  stepperX.moveTo(desiredPositionX);
  stepperY.moveTo(desiredPositionY);


  stepperX.run();
  stepperY.run();
  

  int buttonState = digitalRead(lightTrigger);
  if (buttonState == LOW) {
    delay(50);
    if (lightState == false) {
      lightState = true;
    } else {
      lightState = false;
    }

    while (digitalRead(lightTrigger) == LOW) {
      delay(10);
    }
  }

  
  if (lightState) {
    digitalWrite(lightPin, HIGH); // Turn light on
  } else {
    digitalWrite(lightPin, LOW); // Turn light off
  }
}
