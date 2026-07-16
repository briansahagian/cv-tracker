#include <Servo.h>

Servo panServo;
Servo tiltServo;

// --- MAKERBASE PIN SETUP ---
const int panPin = 15;  // Y+
const int tiltPin = 14; // Y-

int panAngle = 140;
int tiltAngle = 5;

// --- High-Speed Serial Variables ---
const byte numChars = 32;
char receivedChars[numChars]; // Array to hold incoming data
boolean newData = false;      // Flag to track when a full command is received

void setup() {
  Serial.begin(115200);
  
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
  
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void loop() {
  // 1. Constantly check for new serial data without blocking
  recvWithStartEndMarkers();
  
  // 2. If a complete `<...>` packet was received, update the motors
  if (newData == true) {
    parseData();
    panServo.write(panAngle);
    tiltServo.write(tiltAngle);
    newData = false; // Reset the flag
  }
}

// Reads characters one by one without pausing the Arduino
void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1; // Prevent buffer overflow
        }
      } else {
        receivedChars[ndx] = '\0'; // Terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

// Splits the string "95,120" into two separate integers
void parseData() {
  char * strtokIndx; // Pointer used by strtok()

  // Get the first part (Pan) up to the comma
  strtokIndx = strtok(receivedChars, ","); 
  if(strtokIndx != NULL) {
    panAngle = atoi(strtokIndx); // Convert string to integer
  }

  // Get the second part (Tilt) after the comma
  strtokIndx = strtok(NULL, ",");          
  if(strtokIndx != NULL) {
    tiltAngle = atoi(strtokIndx); // Convert string to integer
  }
}