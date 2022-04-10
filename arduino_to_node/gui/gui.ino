#include <Servo.h>

Servo myservo;
int percent = 0;
int prevPercent = 0;
int LED = 13;
int Data;
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


int pot1 = analogRead(A0);
int pot2 = analogRead(A1);
int pot3 = analogRead(A2);
Serial.print(pot1);
Serial.print('a');
Serial.print(pot2);
Serial.print('a');
Serial.println(pot3);


myservo.write(sudut); 
//Serial.print('a');
//Serial.println(sudut);
delay(100);
}
  
