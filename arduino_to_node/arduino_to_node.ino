#include <Servo.h>

Servo myservo;
int percent = 0;
int prevPercent = 0;
int LED = 13;

void setup() {
  myservo.attach(1);
  Serial.begin( 115200 );

}

void loop() {
// if(Serial.available()> 0{
//  
// }
  
  
  int data = analogRead(0);
  percent = map(data,0,1023,0,100);
  Serial.println(data);
//  Serial.println(percent);
//  Serial.println('ok');
//  Serial.println(percent);
  if (percent != prevPercent) {

//    Serial.println(percent);

    prevPercent = percent;


  if (percent>50){
    digitalWrite(LED,HIGH);
    myservo.write(0); 
    delay(200); 
  }
  else{
    digitalWrite(LED,LOW);
    myservo.write(180); 
    delay(200); 
  }

  }

  delay(1000);

}
