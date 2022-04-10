#include "EasyNextionLibrary.h"

EasyNex myNex(Serial1);   // Create an object of EasyNex class with the name < myNex >
// Set as parameter the Serial you are going to use

float temperature_value_c = 0.0; // stores temperature value

uint16_t voltageGraph;   // a variable to store the reading
// for simplicity reasons, we do not use float and we are going to take the measure in millivolts

const int REFRESH_TIME = 100;           // time to refresh the Nextion page every 100 ms
unsigned long refresh_timer = millis();  // timer for refreshing Nextion's page

char tes;

float val;
float C = 29.51; //Constant of straight line (Y = mx + C)
float slope = 542.5; // Slope of straight line (Y = mx + C)
float volt; //voltage read by arduino
float tempC; //final temperature in degree celsius after calibration
float temp1; //temperatuere before calibration
float calibration; //calibration
float Rx; //Resistance of PT100

float R0 = 100.0; //Resistance of minimum temperature to be measured (at 0 degree)
float alpha = 0.00385; // value of alpha from datasheet

const int led1 = 13;
const int led2 = 12;

float getTemperature(int xx) {
  val = analogRead(xx);
  volt = val * 5 / 1023;

  // Converting voltage to resistance
  Rx = volt * slope + C; //y=mx+c

  // Converting resistnace to temperature
  temp1 = (Rx / R0 - 1.0) / alpha; // from Rx = R0(1+alpha*X)
  calibration = 0.3 + (0.005 * temp1); //tolerance for class B PT100
  tempC = temp1 - calibration; // Final temperature in celsius

  return tempC;

  //delay(250);
}
void sendTemperatureToNextion(int xx)
{
  String command = "tsuhu.txt=\"" + String(getTemperature(xx), 1) + "\"";
  Serial1.print(command);
  Serial1.write(0xff);
  Serial1.write(0xff);
  Serial1.write(0xff);
}
void sendTemperatureToNextion1(int xx)
{
  String command = "t4.txt=\"" + String(getTemperature(xx), 1) + "\"";
  Serial1.print(command);
  Serial1.write(0xff);
  Serial1.write(0xff);
  Serial1.write(0xff);
}

void sendTemperatureGraph(int xx) {
  if ((millis() - refresh_timer) > REFRESH_TIME) { //IMPORTANT do not have serial print commands in the loop without a delay
    voltageGraph = map(getTemperature(xx), 0, 100, 0, 255);
    myNex.writeNum("NvoltageGraph.val", voltageGraph);

    refresh_timer = millis();  // Set the timer equal to millis, create a time stamp to start over the "delay"
  }
}

void sendTemperatureGraph1(int xx) {
  if ((millis() - refresh_timer) > REFRESH_TIME) { //IMPORTANT do not have serial print commands in the loop without a delay
    voltageGraph = map(getTemperature(xx), 0, 100, 0, 255);
    myNex.writeNum("va1.val", voltageGraph);

    refresh_timer = millis();  // Set the timer equal to millis, create a time stamp to start over the "delay"
  }
}

void setup()
{
  Serial.begin(115200);
  Serial1.begin(115200);
  myNex.begin(115200); // Begin the object with a baud rate of 9600

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(A0, INPUT); // set A0 pin as INPUT
  pinMode(A1, INPUT);
  digitalWrite(led2, HIGH);
  digitalWrite(led1, LOW);

}

void loop()
{

  static unsigned long timepoint = millis();
  if (millis() - timepoint > 1500) //time interval: 1s
  {
    timepoint = millis();
    //    Serial.print("T1 = ");
    getTemperature(0);
    getTemperature(1);
    Serial.print (getTemperature(0));
    Serial.print('a');
    Serial.println (getTemperature(1));
    sendTemperatureToNextion(0);
    sendTemperatureGraph(0);
    sendTemperatureToNextion1(1);
    sendTemperatureGraph(1);

    if (Serial.available() > 0) {
      tes = Serial.read();
    }
    if (tes == '1') {
      //        Serial.print("Pump: ");
      //        Serial.println("OFF");
      digitalWrite(led2, HIGH);
    } else if (tes == '2') {
      //        Serial.print("Pump: ");
      //        Serial.println("ON");
      digitalWrite(led2, LOW);
    }
    else if (tes == '4') {
      //        Serial.print("Heater: ");
      //        Serial.println("ON");
      digitalWrite(led1, HIGH);
    } else if (tes == '3') {
      //        Serial.print("Heater: ");
      //        Serial.println("OFF");
      digitalWrite(led1, LOW);
    }

  }
}
