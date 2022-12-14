#include <ArduinoJson.h>
#include <Servo.h>
StaticJsonDocument<1024> masterJSON;
String dataIN;
StaticJsonDocument<1024> dataJSON;

Servo myservo;
int percent = 0;
int prevPercent = 0;
int LED = 13;
int Data,mode;
int sudut = 0;
int flag=0;

void setup() {
  myservo.attach(1);
  Serial.begin( 115200 );
  pinMode(LED,OUTPUT);

}

void loop() {
if(Serial.available()>0)
  {
    Data = Serial.read();
  }
  if(Data == '1')
  {
    digitalWrite(LED,LOW);
  }
  else if(Data == '2')
  {
    digitalWrite(LED,HIGH);
  }
  else if(Data == '3')
  {
    sudut=0;
  }
  else if(Data == '4')
  {
    sudut=90;
  }

//Recieve data from mini PC
while(Serial.available()>0){
    static char message[174];
    static unsigned int message_pos = 0;
    char inByte = char(Serial.read());
    if(inByte !='\n'&&(message_pos < 174-1)){
      message[message_pos] = inByte;
      message_pos++;
    }
    else{
      message[message_pos] = '\0';
      dataIN = String (message);
      message_pos = 0;
    }
  }
  DeserializationError master =  deserializeJson(dataJSON, dataIN);
if (master) return;
else mode = dataJSON["MODE"];
if (mode == 1){
  digitalWrite(13,HIGH);
}
else if(mode == 0){
  digitalWrite(13,LOW);
}

int pot1 = analogRead(A0);

masterJSON["T3"] = pot1;
masterJSON["EC"] = analogRead(A1);

//serializeJson(masterJSON,Serial);
//Serial.println();


myservo.write(sudut); 
//Serial.print('a');
//Serial.println(sudut);
delay(100);
}
  
