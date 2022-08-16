#include <ArduinoJson.h>
#include "Adafruit_MPRLS.h"
#include <Wire.h>

#define Buzzer 21
#define redLED 22
#define yellowLED 23
#define greenLED 24
#define BUBBLES 25
#define BUBBLET 26
#define RESET_PIN -1
#define EOC_PIN -1

StaticJsonDocument<1024> slaveJSON;
StaticJsonDocument<1024> dataJSON;
Adafruit_MPRLS mpr = Adafruit_MPRLS(RESET_PIN, EOC_PIN);
String slaveIN, dataIN;
float PDOffset = 0.0;
float PAOffset = 0.0;
float PVOffset = 0.0;
float PDVal, PAVal, PVVal;
bool bsVal;

//DATA IN FROM MINI PC
int mode;
float durations, flowBP, flowSP, volumeSP, mixA, mixB;
bool bypass, alert, sound, start;

//DATA IN FROM SLAVE
float T1, T2, T3, EC, PH, FM;
int VD;
bool BD, HT, CL, V1, V2, V3, V4, V5, V6, V7, V8, V9, V10, V11, V12, V13;
//V12 V BYPASS V13 V DIALISER

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  mpr.begin();
  pinMode(BUBBLES, INPUT);
  pinMode(BUBBLET, INPUT);

  pinMode(Buzzer, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  
  for (int i=1; i<=3; i++){
    PDOffset += mpr.readPressure()/ 68.947572932;
    delay(1000);
  }
  PDOffset /= 3;
  
//  if (error) {
//    Serial.print(F("deserializeJson() failed: "));
//    Serial.println(error.f_str());
//    return;
//  }
}

void loop() {
//Recieve data from mini PC
  if(Serial.available()>0){
    while(!dataIN.endsWith("}")){
      dataIN += char(Serial.read());
    }
  }
  DeserializationError data = deserializeJson(dataJSON, dataIN);

//Parsing data
  mode = dataJSON["MODE"];
  durations = dataJSON["DUR"];
  flowBP = dataJSON["FLOW"][0];
  flowSP = dataJSON["FLOW"][1];
  volumeSP = dataJSON["VOL"];
  mixA = dataJSON["MIX"][0];
  mixB = dataJSON["MIX"][1];
  bypass = dataJSON["BYPS"];
  alert = dataJSON["ALRT"];
  sound = dataJSON["SND"];
  start = dataJSON["START"];

//Recieve data from slave
  if(Serial1.available()>0){
    while(!slaveIN.endsWith("}")){
      slaveIN += char(Serial1.read());
    }
  }
  DeserializationError slave = deserializeJson(slaveJSON, slaveIN);  

//Parsing data
  T1 = slaveJSON["T"][0];
  T2 = slaveJSON["T"][1];
  T3 = slaveJSON["T"][2]; //Temp olah
  EC = slaveJSON["EC"]; //conductivity olah
  PH = slaveJSON["PH"]; //ph olah
  FM = slaveJSON["FM"]; //flowrate dialisat olah
  VD = slaveJSON["VD"];  //bld ipeh, buat alert aja
  BD = slaveJSON["BD"]; //bld damar, buat alert aja
  HT = slaveJSON["HT"]; //heater, boleh ditampililn cuma on/off, ngga juga gpp
  CL = slaveJSON["CL"]; //clamp, alerting
  V1 = slaveJSON["V"][0];
  V2 = slaveJSON["V"][1];
  V3 = slaveJSON["V"][2];
  V4 = slaveJSON["V"][3];
  V5 = slaveJSON["V"][4];
  V6 = slaveJSON["V"][5];
  V7 = slaveJSON["V"][6];
  V8 = slaveJSON["V"][7];
  V9 = slaveJSON["V"][8];
  V10 = slaveJSON["V"][9];
  V11 = slaveJSON["V"][10];
  V12 = slaveJSON["V"][11]; //katup bypass olah
  V13 = slaveJSON["V"][12];
  

//TODO Read Sensor
  PDVal = (mpr.readPressure()/ 68.947572932 - PDOffset) * 51.71492;

  if(digitalRead(BUBBLET)){
    bsVal = digitalRead(BUBBLES);
  }
  if(BD || CL || V12 || VD && sound == 0){
    if(VD == 1) Buzz(VD);
    else if (VD == 2) Buzz(VD);
    else Buzz(3);
  }
  else if (sound == 1){
    Buzz(1);
  }

//Add data bubble and pressure
  slaveJSON["BUBBLE"] = bsVal; //bubble buat alert on/off
  dataJSON["BUBBLE"] = bsVal;
  JsonArray PRESS = slaveJSON.createNestedArray("PRESS");
  PRESS.add(PDVal); //pdval olah
  PRESS.add(PAVal); //arteri pressure olah
  PRESS.add(PVVal); //venous pressure olah

//Send data to mini PC and slave
  serializeJson(dataJSON, Serial1);
  serializeJson(slaveJSON, Serial);
  delay(1000);
}

void Buzz(int level){
  if (level == 1){
    noTone(Buzzer);
    digitalWrite(redLED, LOW);
    digitalWrite(yellowLED, LOW);
    digitalWrite(greenLED, HIGH);
  }
  else if (level == 2){
    tone(Buzzer, 5000, 100);
    digitalWrite(redLED, LOW);
    digitalWrite(yellowLED, HIGH);
    digitalWrite(greenLED, LOW);
  }
  else if (level == 3){
    tone(Buzzer, 10000, 200);
    digitalWrite(redLED, HIGH);
    digitalWrite(yellowLED, LOW);
    digitalWrite(greenLED, LOW);
  }
}
