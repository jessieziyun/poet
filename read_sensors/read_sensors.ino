#include <Wire.h>
#include <BH1750.h>
#include "DHT.h"
#define DHTPIN 7
#define DHTTYPE DHT11

BH1750 lightMeter;

DHT dht(DHTPIN, DHTTYPE);

const int AirValue = 560;
const int WaterValue = 270;
int soilMoistureValue = 0;
int soilmoisturepercent = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  lightMeter.begin();
  dht.begin();
  pinMode(10, INPUT); // Setup for leads off detection LO +
  pinMode(11, INPUT); // Setup for leads off detection LO -

}

void loop() {
  
  delay(1000); // Wait 1s between measurements
  soilMoistureValue = analogRead(A1);
  soilmoisturepercent = map(soilMoistureValue, AirValue, WaterValue, 0, 100);

  if (soilmoisturepercent >= 100)
  {
    Serial.print("100 ");
  }
  else if (soilmoisturepercent <= 0)
  {
    Serial.print("0 ");
  }
  else if (soilmoisturepercent > 0 && soilmoisturepercent < 100)
  {
    Serial.print(soilmoisturepercent);
    Serial.print(" ");
  }
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  Serial.print (h); // humidity
  Serial.print (" ");
  Serial.print (t); // temperature
  Serial.print (" ");
  float lux = lightMeter.readLightLevel();
  Serial.print(lux); // luminosity
  Serial.print (" ");
  Serial.println(analogRead(A0)); // electrical signal
}
