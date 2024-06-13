#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>

const char* WIFI_SSID = "BK_F";
const char* WIFI_PASS = "1234568#*";

const char* FIREBASE_HOST = "pbl5-nhom7-default-rtdb.asia-southeast1.firebasedatabase.app";
const char* FIREBASE_AUTH = "17rYbYhAXzSSEUQCqYJUKBQXSu9uyXAvuALVFJNW";

const int led1 = D0;
const int led2 = D1;
const int led3 = D2;
const int led4 = D3;
const int led_default = D4;

FirebaseData fbdo;

void updateLeds() {
  int led1Status, led2Status, led3Status, led4Status;
  
  Firebase.getInt(fbdo, "/table_orders/Ban1/status");
  led1Status = fbdo.intData();
  Firebase.getInt(fbdo, "/table_orders/Ban2/status");
  led2Status = fbdo.intData();
  Firebase.getInt(fbdo, "/table_orders/Ban3/status");
  led3Status = fbdo.intData();
  Firebase.getInt(fbdo, "/table_orders/Ban4/status");
  led4Status = fbdo.intData();

  bool allZero = (led1Status == 0 && led2Status == 0 && led3Status == 0 && led4Status == 0);
  
  if (allZero) {
    // Check status from tables_destination if all in table_orders are 0
    Firebase.getInt(fbdo, "/tables-destination/Ban1/status");
    led1Status = fbdo.intData();
    Firebase.getInt(fbdo, "/tables-destination/Ban2/status");
    led2Status = fbdo.intData();
    Firebase.getInt(fbdo, "/tables-destination/Ban3/status");
    led3Status = fbdo.intData();
    Firebase.getInt(fbdo, "/tables-destination/Ban4/status");
    led4Status = fbdo.intData();
  }

  digitalWrite(led1, (led1Status == 1 || led1Status == 2) ? HIGH : LOW);
  digitalWrite(led2, (led2Status == 1 || led2Status == 2) ? HIGH : LOW);
  digitalWrite(led3, (led3Status == 1 || led3Status == 2) ? HIGH : LOW);
  digitalWrite(led4, (led4Status == 1 || led4Status == 2) ? HIGH : LOW);

  if (led1Status == 0 && led2Status == 0 && led3Status == 0 && led4Status == 0) {
    digitalWrite(led_default, HIGH);  // Turn on the default LED
  } else {
    digitalWrite(led_default, LOW);   // Turn off the default LED
  }
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

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  pinMode(led_default, OUTPUT);

  digitalWrite(led_default, HIGH); // Turn on the default LED

  updateLeds(); // Initial check
}

void loop() {
  // Update LEDs based on Firebase status
  updateLeds();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
  }

  delay(1000); // Add a delay to avoid rapid polling, adjust as needed
}
