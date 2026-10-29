#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_MCP9808.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_MCP9808 mcp;

#define GREEN_LED 2
#define YELLOW_LED 4
#define RED_LED 6
#define BUZZER_PIN 8

#define WARNING_TEMP 30.0
#define OVERHEAT_TEMP 36.0

#define MAX_RETRIES 3

void setup() {
  Serial.begin(9600);
  Wire.begin();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BUZZER_PIN, HIGH);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED NOT FOUND");
    while (1);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(35, 28);
  display.println("PYROQUADCOM");
  display.display();

  delay(1500);

  if (!mcp.begin(0x18)) {
    Serial.println("MCP9808 NOT FOUND");

    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(25, 28);
    display.println("MCP ERROR");
    display.display();

    while (1);
  }

  Serial.println("System Ready");
  Serial.println("CP2102 SERIAL READY");

  delay(500);
}

void loop() {
  float temperature = 0;
  bool success = false;

  for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    temperature = mcp.readTempC();

    if (temperature > -40.0 && temperature < 125.0) {
      success = true;
      break;
    }

    Serial.print("MCP READ ERROR #");
    Serial.println(attempt);

    delay(300);
  }

  if (!success) {
    Serial.println("MCP READ FAILED AFTER 3 RETRIES");

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, LOW);
    digitalWrite(BUZZER_PIN, HIGH);

    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(20, 25);
    display.println("Sensor Error");
    display.display();

    delay(1000);
    return;
  }

  String status;

  if (temperature < WARNING_TEMP) {
    status = "NORMAL";

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, LOW);
    digitalWrite(BUZZER_PIN, HIGH);

  } else if (temperature < OVERHEAT_TEMP) {
    status = "WARNING";

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, HIGH);
    digitalWrite(RED_LED, LOW);

    digitalWrite(BUZZER_PIN, LOW);
    delay(150);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(850);

  } else {
    status = "OVERHEATING";

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, HIGH);
    digitalWrite(BUZZER_PIN, LOW);
  }

  Serial.print("Temperature: ");
  Serial.print(temperature, 2);
  Serial.println(" C");

  Serial.print("STATUS: ");
  Serial.println(status);

  Serial.print("DATA,");
  Serial.print(temperature, 2);
  Serial.print(",");
  Serial.println(status);

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor(25, 0);
  display.println("TEMPERATURE");

  display.setTextSize(3);
  display.setCursor(8, 18);
  display.print(temperature, 1);

  display.setTextSize(2);
  display.print(" C");

  display.display();

  if (temperature < WARNING_TEMP) {
    delay(1000);
  }
}