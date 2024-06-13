#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>

const char* WIFI_SSID = "BK_F";
const char* WIFI_PASS = "1234568#*";

const char* FIREBASE_HOST = "pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app";
const char* FIREBASE_AUTH = "17rYbYhAXzSSEUQCqYJUKBQXSu9uyXAvuALVFJNW";

const int lightSensor = A0;  // Light sensor connected to analog pin A0
const int buttonPin = D5;    // Button connected to digital pin D5

FirebaseData fbdo;

volatile bool buttonPressed = false; 

void IRAM_ATTR handleButtonPress() {
  buttonPressed = true;
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("Connected to WiFi.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);

  pinMode(buttonPin, INPUT_PULLUP);  // Configure button pin as input with internal pull-up resistor
  attachInterrupt(digitalPinToInterrupt(buttonPin), handleButtonPress, FALLING);  // Attach interrupt to button pin
}

void loop() {
  int lightValue = analogRead(lightSensor);
  Serial.print("Light sensor value: ");
  Serial.println(lightValue);

  if (lightValue <= 550){
    bool lightMaintained = true;
    unsigned long startTime = millis();
    
    // Check light value for 3.5 seconds
    while (millis() - startTime < 2000) {
      lightValue = analogRead(lightSensor);
      if (lightValue > 550) {
        lightMaintained = false;
        break;
      }
      delay(50);  // Small delay to avoid rapid polling
    }

    if (lightMaintained) {
      checkAndUpdateTableStatus();
    }
  }

  if (buttonPressed) {
    buttonPressed = false;
    Serial.println("Button pressed! Resetting status in tables-destination...");
    // No need to call resetDestinationStatus() here
  }

  delay(300);
}

void checkAndUpdateTableStatus() {
  String path_order;
  String path_dest;
  int status;

  for (int i = 1; i <= 4; i++) {
    // Check and update table in table_orders
    path_order = "/table_orders/Ban" + String(i) + "/status";
    if (Firebase.getInt(fbdo, path_order.c_str())) {
      status = fbdo.intData();
      Serial.print("Ban");
      Serial.print(i);
      Serial.print(" status in table_orders: ");
      Serial.println(status);
      
      if (status == 1) {
        delay(10000);  // Wait for 7 seconds before updating
        Firebase.setInt(fbdo, path_order.c_str(), 2);
        Serial.print("Updated Ban");
        Serial.print(i);
        Serial.println(" status to 2 in table_orders");

        // Wait until the status of this table becomes 0
        while (Firebase.getInt(fbdo, path_order.c_str()) && fbdo.intData() != 0) {
          delay(1000);  // Check every second
          Serial.print("Waiting for Ban");
          Serial.print(i);
          Serial.println(" status to become 0 in table_orders");
        }
        return;  // Exit the function after updating the status and waiting
      }
    } else {
      Serial.print("Failed to get status for Ban");
      Serial.print(i);
      Serial.println(" in table_orders");
    }

    // Check and update table in tables_destination
    path_dest = "/tables-destination/Ban" + String(i) + "/status";
    if (Firebase.getInt(fbdo, path_dest.c_str())) {
      status = fbdo.intData();
      Serial.print("Ban");
      Serial.print(i);
      Serial.print(" status in tables_destination: ");
      Serial.println(status);
      
      if (status == 1) {
        delay(7000);  // Wait for 7 seconds before updating
        Firebase.setInt(fbdo, path_dest.c_str(), 2);
        Serial.print("Updated Ban");
        Serial.print(i);
        Serial.println(" status to 2 in tables_destination");

        // Wait for the button press to change the status to 0
        while (!buttonPressed) {
          delay(100);  // Small delay to avoid rapid polling
        }
        buttonPressed = false;  // Reset button press status

        Firebase.setInt(fbdo, path_dest.c_str(), 3);
        delay(7500);
        Firebase.setInt(fbdo, path_dest.c_str(), 0);
        Serial.print("Reset Ban");
        Serial.print(i);
        Serial.println(" status to 0 in tables_destination");

        return;  // Exit the function after updating the status and waiting
      }
    } else {
      Serial.print("Failed to get status for Ban");
      Serial.print(i);
      Serial.println(" in tables_destination");
    }
  }
}
