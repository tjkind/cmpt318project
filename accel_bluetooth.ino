#include <Arduino.h>
#include <SPI.h>
#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_LSM303.h>
#include <String.h>
#include "BluefruitConfig.h"

#if SOFTWARE_SERIAL_AVAILABLE
#include <SoftwareSerial.h>
#endif

#define FACTORYRESET_ENABLE         0
#define MINIMUM_FIRMWARE_VERSION    "0.6.6"
#define MODE_LED_BEHAVIOUR          "MODE"
#define BLUEFRUIT_UART_MODE_PIN         -1   // Not used with FLORA
#define BLUEFRUIT_UART_CTS_PIN          -1   // Not used with FLORA
#define BLUEFRUIT_UART_RTS_PIN          -1   // Not used with Flora

#define BLUEFRUIT_HWSERIAL_NAME Serial1

Adafruit_BluefruitLE_UART ble(BLUEFRUIT_HWSERIAL_NAME, BLUEFRUIT_UART_MODE_PIN);
Adafruit_LSM303 lsm;
long time_stamp;
long start_time;
//String move_name;

// A small helper
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}

void setup(void)
{
  Serial.begin(115200);

  lsm.begin();

  Serial.print(F("Initialising the Bluefruit LE module: "));
  if ( !ble.begin(VERBOSE_MODE) )
  {
    error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
  }
  Serial.println( F("OK!") );

  Serial.println("Requesting Bluefruit info:");
  ble.info();
  ble.verbose(false);  // debug info is a little annoying after this point!
  ble.echo(false);
  /* Wait for connection */
  while (! ble.isConnected()) {
    delay(500);
  }

  // LED Activity command is only supported from 0.6.6
  if ( ble.isVersionAtLeast(MINIMUM_FIRMWARE_VERSION) )
  {
    // Change Mode LED Activity
    Serial.println(F("******************************"));
    Serial.println(F("Change LED activity to " MODE_LED_BEHAVIOUR));
    ble.sendCommandCheckOK("AT+HWModeLED=" MODE_LED_BEHAVIOUR);
    Serial.println(F("******************************"));
  }

  ble.setMode(BLUEFRUIT_MODE_DATA);

}

void loop(void)
{
  String move_name = "";
  while (!ble.available()) {
    delay(10);
  }
  while ( ble.available())
  {
    move_name += (char)ble.read();
    //move_name += (char)c;
  }
  move_name.trim();
  start_time = millis();
  Serial.print("**** ");
  Serial.print(millis());
  Serial.println(" ****");
  time_stamp = millis() - start_time;
  while (time_stamp < 3500) {
    lsm.read();
    ble.print(move_name); ble.print(", ");
    ble.print((int)lsm.accelData.x); ble.print(", ");
    delay(5);
    ble.print((int)lsm.accelData.y); ble.print(", ");
    delay(5);
    ble.print((int)lsm.accelData.z); ble.print(", ");
    delay(5);
    ble.println(time_stamp);
//    delay(1);
//    Serial.print("Accel X: "); Serial.print(lsm.accelData.x); Serial.print(" ");
//    Serial.print("Y: "); Serial.print((int)lsm.accelData.y);       Serial.print(" ");
//    Serial.print("Z: "); Serial.println((int)lsm.accelData.z);     Serial.print(" ");
    delay(20);
    time_stamp = millis() - start_time;
  }
  delay(10);
  Serial.println("done done");
  Serial.print("**** ");
  Serial.print(time_stamp);
  Serial.print(" ");
  Serial.print(move_name);
  Serial.println(" ****");
  while ( ble.available())
  {
    int c = ble.read();
    move_name += (char)c;
  }
}
