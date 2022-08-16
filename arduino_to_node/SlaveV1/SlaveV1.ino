#include <Fuzzy.h>
#include <Wire.h>
#include <DFRobot_PH.h>
#include <DFRobot_EC.h>
#include <EEPROM.h>
#include <ArduinoJson.h>
#include <AccelStepper.h>

//SENSOR
#define T1 14
#define T2 15
#define T3 16
#define EC 17
#define PH 18
#define FM 19
#define BLD0 20
#define BLD1 21
#define BLD2 22
#define BLD3 13
#define BLD_OUT 23
#define LDR1 24
#define LDR2 25
#define LDR3 26
#define LDR4 27

//AKTUATOR
#define P1 2 //Pump RO
#define P2 3 //Pump Heater
#define P3 4 //Pump Asam
#define P4 5 //Pump Basa
#define P5 6 //Pump Dialisat
#define HEATER 7
#define CLAMP 8
#define BP_PUL 9
#define BP_DIR 10
#define SP_PUL 11
#define SP_DIR 12
#define V1 29 //Valve air
#define V2 30 //Valve asam
#define V3 31 //Valve basa
#define V4 32 //Valve 1 CH
#define V5 33 //Valve 2 CH
#define V6 34 //Valve 3 CH
#define V7 35 //Valve 4 CH
#define V8 36 //Valve 5 CH
#define V9 37 //Valve 6 CH
#define V10 38 //Valve 7 CH
#define V11 39 //Valve 8 CH
#define BYPASS1 40 //Dialyzer
#define BYPASS2 41 //Drain
#define VDIAL 28

// hill
#define PWM_MIN 0     
#define PWM_MAX 90    
#define PWM_START 40 

StaticJsonDocument<1024> masterJSON;
StaticJsonDocument<1024> slaveJSON;
DFRobot_PH ph;
DFRobot_EC ec;
AccelStepper pumpSP(1,BP_PUL,BP_DIR);
AccelStepper pumpBP(1,SP_PUL,SP_DIR);

String masterIN, slaveOUT;

//Var from master
int mode;
float durations, flowBP, flowSP, volumeSP, mixA, mixB;
bool bypassIN, alert, sound, start, bubble;

//Var to send to master
float Ts1, Ts2, Ts3, ECs, PHs, FMs;
int VD;
bool BD, HT, CL, V1s, V2s, V3s, V4s, V5s, V6s, V7s, V8s, V9s, V10s, V11s, V12s, V13s;
//V12 V BYPASS V13 V DIALISER

float T1Val,T2Val,T3Val,flowRate, ECVal, PHVal; 
float cf = 75;
float slope = 0.0717;
float C = 52.134;
float Ro = 100.0;
float alpha = 0.00385;

float timeb_sekarang, timea_sekarang, timeb_sebelum, timea_sebelum; 
float db, da, c, d; 
int duty = 1;
int pwm1 = PWM_START;
int pwm2 = PWM_START;
float pa;
float pb;

bool condition = false;
bool interval  = false;

int LDR1Val, LDR2Val, LDR3Val, LDR4Val, max1, max2, max3, max4, riskLevel, 
s1, s2, s3, s4, ss1, ss2, ss3, ss4, val;

bool VL1 = 0;
bool VL2 = 0;
bool VL3 = 0;

bool VL4 = 1; 
bool VL5 = 1; 
bool VL6 = 0; 
bool VL7 = 1; 
bool VL8 = 0; 
bool VL9 = 1; 
bool VL10 = 1; 
bool VL11 = 1; 

bool VL12 = 1;
bool VL13 = 0;
bool Rinse = false, Drain = false, Preparation = false, Normal = false;

int SR = 0, temp = 0, i = 0;

float stepBP, durationBP, stepSP, dosageSP;

long stp;

volatile byte pulseCount = 0;

unsigned long lastMillis = 0, oldTime = 0, current_time = 0, currentMillis = 0, a = 0, b = 0;

Fuzzy *fuzzyBypass = new Fuzzy();

// FuzzyInputTemperature
FuzzySet *tempLow = new FuzzySet(34, 34, 35, 37);
FuzzySet *tempMed = new FuzzySet(36, 37.5, 37.5, 39);
FuzzySet *tempHig = new FuzzySet(38, 40, 41, 41);

// FuzzyInputConductivity
FuzzySet *cdLow = new FuzzySet(10, 10, 11.5, 13.5);
FuzzySet *cdMed = new FuzzySet(12, 14.25, 14.25, 16.5);
FuzzySet *cdHig = new FuzzySet(15.31, 18.15, 18.85, 21.69);

// FuzzyInputpH
FuzzySet *phLow = new FuzzySet(4, 4, 4, 6.5);
FuzzySet *phMed = new FuzzySet(6, 7.2, 7.2, 8.4);
FuzzySet *phHig = new FuzzySet(7.9, 10, 10, 10);

// FuzzyOutput
FuzzySet *Close = new FuzzySet(-0.5, -0.5, 0, 0.75);
FuzzySet *Open  = new FuzzySet(0.25, 1, 1.5, 1.5);

Fuzzy *fuzzyPump = new Fuzzy();

// FuzzyInputFlow
FuzzySet *flowVLow  = new FuzzySet(200, 200, 300, 380);
FuzzySet *flowLow   = new FuzzySet(350, 410, 410, 480);
FuzzySet *flowMed   = new FuzzySet(470, 500, 500, 530);
FuzzySet *flowHigh  = new FuzzySet(520, 590, 590, 650);
FuzzySet *flowVHigh = new FuzzySet(620, 700, 800, 800);

// FuzzyOutputPWM
FuzzySet *lowSpeed = new FuzzySet(150, 150, 168, 186);
FuzzySet *lomSpeed = new FuzzySet(179, 193, 193, 208);
FuzzySet *medSpeed = new FuzzySet(215, 230, 230, 240);
FuzzySet *mehSpeed = new FuzzySet(234, 245, 245, 255);
FuzzySet *higSpeed = new FuzzySet(245, 257, 280, 280);

Fuzzy *fuzzyBLD = new Fuzzy();

// FuzzyInputRed
FuzzySet *R_LOW   = new FuzzySet(0, 0, 0, 85);
FuzzySet *R_MED   = new FuzzySet(50, 125, 125, 200);
FuzzySet *R_HIGH  = new FuzzySet(155, 255, 255, 255);

// FuzzyInputGreen
FuzzySet *G_LOW   = new FuzzySet(0, 0, 0, 85);
FuzzySet *G_MED   = new FuzzySet(50, 125, 125, 200);
FuzzySet *G_HIGH  = new FuzzySet(155, 255, 255, 255);

// FuzzyInputBlue
FuzzySet *B_LOW   = new FuzzySet(0, 0, 0, 85);
FuzzySet *B_MED   = new FuzzySet(50, 125, 125, 200);
FuzzySet *B_HIGH  = new FuzzySet(155, 255, 255, 255);

// FuzzyOutputBLD
FuzzySet *NoBlood = new FuzzySet(0, 50, 50, 50); 
FuzzySet *Blood   = new FuzzySet(50, 100, 100, 100);

void setup(){
  Serial.begin(115200);
  Serial1.begin(115200);
  ph.begin();
  ec.begin();
  pumpBP.setMaxSpeed(2000);
  pumpSP.setMaxSpeed(1000);
  
  pinMode(T1, INPUT);
  pinMode(T2, INPUT);
  pinMode(T3, INPUT);
  pinMode(EC, INPUT);
  pinMode(PH, INPUT);
  pinMode(FM, INPUT);
  pinMode(BLD0, OUTPUT);
  pinMode(BLD1, OUTPUT);
  pinMode(BLD2, OUTPUT);
  pinMode(BLD3, OUTPUT);
  pinMode(BLD_OUT, INPUT);
  
  pinMode(LDR1, INPUT);
  pinMode(LDR2, INPUT);
  pinMode(LDR3, INPUT);
  pinMode(LDR4, INPUT);  

  pinMode(P1, OUTPUT);
  pinMode(P2, OUTPUT);
  pinMode(P3, OUTPUT);
  pinMode(P4, OUTPUT);
  pinMode(P5, OUTPUT);
  pinMode(HEATER, OUTPUT);
  pinMode(BP_PUL, OUTPUT);
  pinMode(BP_DIR, OUTPUT);
  pinMode(SP_PUL, OUTPUT);
  pinMode(SP_DIR, OUTPUT);
  pinMode(V1, OUTPUT);
  pinMode(V2, OUTPUT);
  pinMode(V3, OUTPUT);
  pinMode(V4, OUTPUT);
  pinMode(V5, OUTPUT);
  pinMode(V6, OUTPUT);
  pinMode(V7, OUTPUT);
  pinMode(V8, OUTPUT);
  pinMode(V9, OUTPUT);
  pinMode(V10, OUTPUT);
  pinMode(V11, OUTPUT);
  pinMode(BYPASS1, OUTPUT);
  pinMode(BYPASS2, OUTPUT);
  pinMode(VDIAL, OUTPUT);
  pinMode(CLAMP, OUTPUT);

  digitalWrite(FM, HIGH);
  digitalWrite(BLD0, HIGH);
  digitalWrite(BLD1, LOW);
  pumpSP.setCurrentPosition(0);
  pumpBP.setCurrentPosition(0);
  attachInterrupt(digitalPinToInterrupt(FM), pulseCounter, FALLING);

  // FuzzyInput Temperature
  FuzzyInput *temp = new FuzzyInput(1);
  temp->addFuzzySet(tempLow);
  temp->addFuzzySet(tempMed);
  temp->addFuzzySet(tempHig);
  fuzzyBypass->addFuzzyInput(temp);

  // FuzzyInput Conductivity
  FuzzyInput *cd = new FuzzyInput(2);
  cd->addFuzzySet(cdLow);
  cd->addFuzzySet(cdMed);
  cd->addFuzzySet(cdHig);
  fuzzyBypass->addFuzzyInput(cd);

  // FuzzyInput pH
  FuzzyInput *ph = new FuzzyInput(3);
  ph->addFuzzySet(phLow);
  ph->addFuzzySet(phMed);
  ph->addFuzzySet(phHig);
  fuzzyBypass->addFuzzyInput(ph);

  // FuzzyOutput Valve
  FuzzyOutput *valve = new FuzzyOutput(1);
  valve->addFuzzySet(Close);
  valve->addFuzzySet(Open);
  fuzzyBypass->addFuzzyOutput(valve);  

  // FuzzyInput
  FuzzyInput *flow = new FuzzyInput(1);
  flow->addFuzzySet(flowVLow);
  flow->addFuzzySet(flowLow);
  flow->addFuzzySet(flowMed);
  flow->addFuzzySet(flowHigh);
  flow->addFuzzySet(flowVHigh);
  fuzzyPump->addFuzzyInput(flow);

  // FuzzyOutput
  FuzzyOutput *pump = new FuzzyOutput(1);
  pump->addFuzzySet(lowSpeed);
  pump->addFuzzySet(lomSpeed);
  pump->addFuzzySet(medSpeed);
  pump->addFuzzySet(mehSpeed);
  pump->addFuzzySet(higSpeed);
  fuzzyPump->addFuzzyOutput(pump);
  
  // FuzzyInputRed
  FuzzyInput *RED = new FuzzyInput(1);
  RED->addFuzzySet(R_LOW);
  RED->addFuzzySet(R_MED);
  RED->addFuzzySet(R_HIGH);
  fuzzyBLD->addFuzzyInput(RED);

  // FuzzyInputGreen
  FuzzyInput *GREEN = new FuzzyInput(2);
  GREEN->addFuzzySet(G_LOW);
  GREEN->addFuzzySet(G_MED);
  GREEN->addFuzzySet(G_HIGH);
  fuzzyBLD->addFuzzyInput(GREEN);

  // FuzzyInputBlue
  FuzzyInput *BLUE = new FuzzyInput(3);
  BLUE->addFuzzySet(B_LOW);
  BLUE->addFuzzySet(B_MED);
  BLUE->addFuzzySet(B_HIGH);
  fuzzyBLD->addFuzzyInput(BLUE);

  // FuzzyOutputBLD
  FuzzyOutput *detection = new FuzzyOutput(1);
  detection->addFuzzySet(Blood);
  detection->addFuzzySet(NoBlood);
  fuzzyBLD->addFuzzyOutput(detection);

  // FuzzyRule Bypass
  FuzzyRuleAntecedent *tempLoww = new FuzzyRuleAntecedent();
  tempLoww->joinSingle(tempLow);
  FuzzyRuleConsequent *thenvalveOpen = new FuzzyRuleConsequent();
  thenvalveOpen->addOutput(Open);

  FuzzyRule *fuzzyRule1 = new FuzzyRule(1, tempLoww,thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule1);

  FuzzyRuleAntecedent *tempHigh = new FuzzyRuleAntecedent();
  tempHigh->joinSingle(tempHig);
  
  FuzzyRule *fuzzyRule2 = new FuzzyRule(2, tempHigh,thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule2);

  FuzzyRuleAntecedent *iftempMedANDcdLow = new FuzzyRuleAntecedent();
  iftempMedANDcdLow->joinWithAND(tempMed, cdLow);

  FuzzyRule *fuzzyRule3 = new FuzzyRule(3, iftempMedANDcdLow,thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule3);

  FuzzyRuleConsequent *thenvalveClose = new FuzzyRuleConsequent();
  thenvalveClose->addOutput(Close);

  FuzzyRuleAntecedent *phmed = new FuzzyRuleAntecedent();
  phmed->joinSingle(phMed);

  FuzzyRuleAntecedent *iftempMedANDcdHig = new FuzzyRuleAntecedent();
  iftempMedANDcdHig->joinWithAND(tempMed, cdHig);

  FuzzyRule *fuzzyRule4= new FuzzyRule(4, iftempMedANDcdHig,thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule4);

  FuzzyRuleAntecedent *iftempMedANDcdMed = new FuzzyRuleAntecedent();
  iftempMedANDcdMed->joinWithAND(tempMed, cdMed);

  FuzzyRuleAntecedent *iftempMedANDcdMedANDphLow = new FuzzyRuleAntecedent();
  iftempMedANDcdMedANDphLow->joinWithAND(iftempMedANDcdMed, phLow);
  
  FuzzyRule *fuzzyRule5 = new FuzzyRule(5, iftempMedANDcdMedANDphLow, thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule5);

  FuzzyRuleAntecedent *iftempMedANDcdMedANDphHigh = new FuzzyRuleAntecedent();
  iftempMedANDcdMedANDphHigh->joinWithAND(iftempMedANDcdMed, phHig);
  
  FuzzyRule *fuzzyRule6 = new FuzzyRule(6, iftempMedANDcdMedANDphHigh, thenvalveOpen);
  fuzzyBypass->addFuzzyRule(fuzzyRule6);

  FuzzyRuleAntecedent *iftempMedANDcdMedANDphMed = new FuzzyRuleAntecedent();
  iftempMedANDcdMedANDphMed->joinWithAND(iftempMedANDcdMed, phMed);
  
  FuzzyRule *fuzzyRule7 = new FuzzyRule(7, iftempMedANDcdMedANDphMed, thenvalveClose);
  fuzzyBypass->addFuzzyRule(fuzzyRule7);  

  // FuzzyRulePump
  FuzzyRuleAntecedent *flowVlow = new FuzzyRuleAntecedent();
  flowVlow->joinSingle(flowVLow);
  
  FuzzyRuleConsequent *thenPWMPH = new FuzzyRuleConsequent();
  thenPWMPH->addOutput(higSpeed);

  FuzzyRule *fuzzyRules1 = new FuzzyRule(1, flowVlow,thenPWMPH);
  fuzzyPump->addFuzzyRule(fuzzyRules1);

  FuzzyRuleAntecedent *flowlow = new FuzzyRuleAntecedent();
  flowlow->joinSingle(flowLow);
  
  FuzzyRuleConsequent *thenPWMPL = new FuzzyRuleConsequent();
  thenPWMPL->addOutput(mehSpeed);

  FuzzyRule *fuzzyRules2 = new FuzzyRule(2, flowlow,thenPWMPL);
  fuzzyPump->addFuzzyRule(fuzzyRules2);

  FuzzyRuleAntecedent *flowmed = new FuzzyRuleAntecedent();
  flowmed->joinSingle(flowMed);
  
  FuzzyRuleConsequent *thenPWMZ = new FuzzyRuleConsequent();
  thenPWMZ->addOutput(medSpeed);

  FuzzyRule *fuzzyRules3 = new FuzzyRule(3, flowmed,thenPWMZ);
  fuzzyPump->addFuzzyRule(fuzzyRules3);

  FuzzyRuleAntecedent *flowhigh = new FuzzyRuleAntecedent();
  flowhigh->joinSingle(flowHigh);
  
  FuzzyRuleConsequent *thenPWMNL = new FuzzyRuleConsequent();
  thenPWMNL->addOutput(lomSpeed);

  FuzzyRule *fuzzyRules4 = new FuzzyRule(4, flowhigh,thenPWMNL);
  fuzzyPump->addFuzzyRule(fuzzyRules4);

  FuzzyRuleAntecedent *flowVhigh = new FuzzyRuleAntecedent();
  flowVhigh->joinSingle(flowVHigh);
  
  FuzzyRuleConsequent *thenPWMNH = new FuzzyRuleConsequent();
  thenPWMNH->addOutput(lowSpeed);

  FuzzyRule *fuzzyRules5 = new FuzzyRule(5, flowVhigh,thenPWMNH);
  fuzzyPump->addFuzzyRule(fuzzyRules5);

  // Fuzzy RuleBLD
  FuzzyRuleConsequent *bloodDetected = new FuzzyRuleConsequent();
  bloodDetected->addOutput(Blood);
  FuzzyRuleConsequent *noBlood = new FuzzyRuleConsequent();
  noBlood->addOutput(NoBlood);

  // Red Low
  FuzzyRuleAntecedent *ifRedLow = new FuzzyRuleAntecedent();
  ifRedLow->joinSingle(R_LOW);
  FuzzyRule *fuzzyRule01 = new FuzzyRule(1, ifRedLow, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule01);

  // Red Medium
  //// Green Low
  FuzzyRuleAntecedent *ifRMGL = new FuzzyRuleAntecedent();
  ifRMGL->joinWithAND(R_MED, G_LOW);

  ////// Blue Low
  FuzzyRuleAntecedent *BL = new FuzzyRuleAntecedent();
  BL->joinSingle(B_LOW);
  
  FuzzyRuleAntecedent *ifRMGLBL = new FuzzyRuleAntecedent();
  ifRMGLBL->joinWithAND(ifRMGL, BL);
  FuzzyRule *fuzzyRule02 = new FuzzyRule(2, ifRMGLBL, bloodDetected);
  fuzzyBLD->addFuzzyRule(fuzzyRule02);

  ////// Blue Medium
  FuzzyRuleAntecedent *BM = new FuzzyRuleAntecedent();
  BM->joinSingle(B_MED);
  
  FuzzyRuleAntecedent *ifRMGLBM = new FuzzyRuleAntecedent();
  ifRMGLBM->joinWithAND(ifRMGL, BM);
  FuzzyRule *fuzzyRule03 = new FuzzyRule(3, ifRMGLBM, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule03);

  ////// Blue High
  FuzzyRuleAntecedent *BH = new FuzzyRuleAntecedent();
  BH->joinSingle(B_HIGH);
  
  FuzzyRuleAntecedent *ifRMGLBH = new FuzzyRuleAntecedent();
  ifRMGLBH->joinWithAND(ifRMGL, BH);
  FuzzyRule *fuzzyRule04 = new FuzzyRule(4, ifRMGLBH, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule04);

  ////Green Medium
  FuzzyRuleAntecedent *ifRMGM = new FuzzyRuleAntecedent();
  ifRMGM->joinWithAND(R_MED, G_MED);
  FuzzyRule *fuzzyRule05 = new FuzzyRule(5, ifRMGM, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule05);

  ////Green High
  FuzzyRuleAntecedent *ifRMGH = new FuzzyRuleAntecedent();
  ifRMGH->joinWithAND(R_MED, G_HIGH);
  FuzzyRule *fuzzyRule06 = new FuzzyRule(6, ifRMGH, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule06);

  //Red High
  ////Green Low
  FuzzyRuleAntecedent *ifRHGL = new FuzzyRuleAntecedent();
  ifRHGL->joinWithAND(R_HIGH, G_LOW);

  //////Blue Low 
  FuzzyRuleAntecedent *ifRHGLBL = new FuzzyRuleAntecedent();
  ifRHGLBL->joinWithAND(ifRHGL, BL);
  FuzzyRule *fuzzyRule07 = new FuzzyRule(7, ifRHGLBL, bloodDetected);
  fuzzyBLD->addFuzzyRule(fuzzyRule07);

  //////Blue Medium  
  FuzzyRuleAntecedent *ifRHGLBM = new FuzzyRuleAntecedent();
  ifRHGLBM->joinWithAND(ifRHGL, BM);
  FuzzyRule *fuzzyRule08 = new FuzzyRule(8, ifRHGLBL, bloodDetected);
  fuzzyBLD->addFuzzyRule(fuzzyRule08);

  //////Blue High
  FuzzyRuleAntecedent *ifRHGLBH = new FuzzyRuleAntecedent();
  ifRHGLBH->joinWithAND(ifRHGL, BH);
  FuzzyRule *fuzzyRule09 = new FuzzyRule(9, ifRHGLBH, noBlood); 
  fuzzyBLD->addFuzzyRule(fuzzyRule09);

  ////Green Medium
  FuzzyRuleAntecedent *ifRHGM = new FuzzyRuleAntecedent();
  ifRHGM->joinWithAND(R_HIGH, G_MED);

  //////Blue Low
  FuzzyRuleAntecedent *ifRHGMBL = new FuzzyRuleAntecedent();
  ifRHGMBL->joinWithAND(ifRHGM, BL);
  FuzzyRule *fuzzyRule10 = new FuzzyRule(10, ifRHGLBL, bloodDetected);
  fuzzyBLD->addFuzzyRule(fuzzyRule10);

  //////Blue Medium
  FuzzyRuleAntecedent *ifRHGMBM = new FuzzyRuleAntecedent();
  ifRHGMBM->joinWithAND(ifRHGM, BM);
  FuzzyRule *fuzzyRule11 = new FuzzyRule(11, ifRHGLBL, bloodDetected);
  fuzzyBLD->addFuzzyRule(fuzzyRule11);

  //////Blue High
  FuzzyRuleAntecedent *ifRHGMBH = new FuzzyRuleAntecedent();
  ifRHGMBH->joinWithAND(ifRHGM, BH);
  FuzzyRule *fuzzyRule12 = new FuzzyRule(12, ifRHGLBH, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule12);

  ////Green High
  FuzzyRuleAntecedent *ifRHGH = new FuzzyRuleAntecedent();
  ifRHGH->joinWithAND(R_HIGH, G_HIGH);
  FuzzyRule *fuzzyRule13 = new FuzzyRule(13, ifRHGH, noBlood);
  fuzzyBLD->addFuzzyRule(fuzzyRule13);
}

void loop(){
  if(Serial1.available()>0){
    while(!masterIN.endsWith("}")){
      masterIN += char(Serial1.read());
    }
  }
  DeserializationError master = deserializeJson(masterJSON, masterIN);  

//Data from master
  mode = masterJSON["MODE"];
  durations = masterJSON["DUR"];
  flowBP = masterJSON["FLOW"][0];
  flowSP = masterJSON["FLOW"][1];
  volumeSP = masterJSON["VOL"];
  mixA = masterJSON["MIX"][0];
  mixB = masterJSON["MIX"][1];
  bypassIN= masterJSON["BYPS"];
  alert = masterJSON["ALRT"];
  sound = masterJSON["SND"];
  start = masterJSON["START"];
  bubble = masterJSON["BUBBLE"];

  if (mode == 1){ //Normal
    Rinse = false; Drain = false; Normal = true; Preparation = false; //PWM250
  }
  else if (mode == 2){ //Drain
    Rinse = false; Drain = true; Normal = false; Preparation = false; //PWM300
  }
  else if (mode == 3){ //Rinse
    Rinse = true; Drain = false; Normal = false; Preparation = false; //PWM250 
  }
  else if (mode == 4){ //Preparation
    Rinse = false; Drain = false; Normal = false; Preparation = true; //PWM250
  }

  if (Rinse||Drain||Preparation){
    analogWrite(P1,200);
    analogWrite(P2,200);
    analogWrite(P3,200);
    analogWrite(P4,200);
    analogWrite(P5,200);
    bukaValve();
  }

  if (Normal && start && !condition){
    lastMillis = millis(); //start timer;
    interval=true;
    condition =true;
  }

  if (interval && (millis() - lastMillis <= durations * 1000)){ 
    analogWrite(P1, 250);
    analogWrite(P2, 250);
    readBP();
    readSP();
    valves();
    Seq ();
    readSensor();
    hamSensor();
    bypassValve();
    BLD();
  }
  else{
    temp = 0;
    pumpSP.setCurrentPosition(0);
    pumpBP.setCurrentPosition(0);
    // analogWrite(P1,0);
    // analogWrite(P2,0);
    // analogWrite(P3,0);
    // analogWrite(P4,0);
    // analogWrite(P5,0);
    // bukaValve();
  }

  persenTime();
  
  JsonArray T = slaveJSON.createNestedArray("T");
  T.add(T1Val);
  T.add(T2Val);
  T.add(T3Val);
  slaveJSON["EC"] = ECVal;
  slaveJSON["PH"] = PHVal;
  slaveJSON["FM"] = flowRate;
  slaveJSON["VD"] = riskLevel;
  slaveJSON["BD"] = BD;
  slaveJSON["HT"] = 1;
  slaveJSON["CL"] = 0;

  JsonArray V = slaveJSON.createNestedArray("V");
  V.add(VL1);
  V.add(VL2);
  V.add(VL3);
  V.add(VL4);
  V.add(VL5);
  V.add(VL6);
  V.add(VL7);
  V.add(VL8);
  V.add(VL8);
  V.add(VL10);
  V.add(VL11);
  V.add(VL12);
  V.add(VL13);
  //V12 V BYPASS V13 V DIALISER

  if(millis() - oldTime >=1000){
    detachInterrupt(digitalPinToInterrupt(FM));
    flowRate = ((1000.0/(millis()-oldTime))*pulseCount)/cf*1000;
    oldTime = millis();
    pulseCount = 0;
    attachInterrupt(digitalPinToInterrupt(FM), pulseCounter, FALLING);
    speedP5();
    serializeJson(slaveJSON, Serial1);
  }

  if(bubble) digitalWrite(CLAMP, HIGH);
  else digitalWrite(CLAMP, LOW);

  ph.calibration(analogRead(PH)/1024.0*3300,T3Val);
  ec.calibration(analogRead(EC)/1024.0*3300,T3Val);  
}

void pump(){
    analogWrite(P3, pwm2); //ENA P3 ASAM
    analogWrite(P4, pwm1); //ENB P4 BASA
}

void writePWM1(){
  if(pwm1 > PWM_MAX) pwm1 = PWM_MAX;
  if(pwm1 < PWM_MIN) pwm1 = PWM_MIN;
}

void writePWM2(){
  if(pwm2 > PWM_MAX) pwm2 = PWM_MAX;
  if(pwm2 < PWM_MIN) pwm2 = PWM_MIN;
}

void mix(){
  pa = mixA  / 100;//3688 NUMBER MIX A
  pb = mixB / 100;//2013 NUMBER1 MIX B
  pump();
  static unsigned long timepoint = millis();
  if(millis()-timepoint>=100){
    timepoint = millis();
    mppt();    
    perbandingan();
  }

  static unsigned long timepoint1 = millis();
  if(millis()-timepoint1>=120000){
    timepoint1 = millis();
    perbandingan();
    c=0;
    d=0;
  }
}

void perbandingan(){ 
  float cairanb = pa / (pa + pb + pa * pb) * 450 / 10;
  float cairana = pb / (pa + pb + pa * pb) * 450 / 10;
  float b = cairanb;
  float a= cairana;
  
  timeb_sekarang = b;
  timea_sekarang = a;
  db = timeb_sekarang - timeb_sebelum;
  da = timea_sekarang - timea_sebelum;

  c = c + 0.1;
  d = d + 0.1;
}

void mppt (){
  if(db > 0 ){
    if (da > 0 ){
      pwm1 = PWM_START;
      pwm2 = PWM_START;
      timeb_sebelum = c;
      timea_sebelum = d;
      writePWM1();
      writePWM2();
      digitalWrite(V4,HIGH);
      digitalWrite(V3,HIGH);
    }

    if (da <= 0){
      pwm1  = PWM_START;
      pwm2 -= duty ;
      timeb_sebelum = c;
      timea_sebelum = d;
      writePWM1();
      writePWM2();
      digitalWrite(V4,HIGH);
      digitalWrite(V3,LOW);    
    }
  }

  if(db < 0){
    if(da > 0){
      pwm1 -= duty;
      pwm2  = PWM_START;
      timeb_sebelum = c;
      timea_sebelum = d;
      writePWM1();
      writePWM2();
      digitalWrite(V4,LOW);
      digitalWrite(V3,HIGH);
    }

    if (da <= 0){
      pwm1 -= duty;
      pwm2 -= duty ;
      timeb_sebelum = c;
      timea_sebelum = d;
      writePWM1();
      writePWM2();
      digitalWrite(V4,LOW);
      digitalWrite(V3,LOW);
    }
  }
}

void readSensor(){
  T1Val = getTemperature(T1);
  T2Val = getTemperature(T2);
  T3Val = getTemperature(T3);
  if(T3Val <= 36.0 ) {
    digitalWrite(HEATER, HIGH);
  }
  else if (T3Val >= 38.0){
    digitalWrite(HEATER, LOW);
  }
  ECVal = ph.readPH(analogRead(PH)/1024.0*3300,T3Val);
  PHVal = ec.readEC(analogRead(EC)/1024.0*3300,T3Val);
  LDR1Val = analogRead(LDR1);
  LDR2Val = analogRead(LDR2);
  LDR3Val = analogRead(LDR3);
  LDR4Val = analogRead(LDR4);  
}

float getTemperature(int T){
  float Rx = analogRead(T)/1.024*3.3*slope+C;
  float temp1 = (Rx/Ro-1)/alpha;
  float calT = 0.3+(0.005*temp1);
  return temp1-calT;
}

void hamSensor(){
  if (LDR1Val > max1){
    max1 = LDR1Val;
  }
  if (LDR2Val > max2){
    max2 = LDR2Val;
  }
  if (LDR3Val > max3){
    max3 = LDR3Val;
  }
  if (LDR4Val > max4){
    max4 = LDR4Val;
  }

  if(LDR1Val < max1*70/100){
    s1 = 1;
    ss1 = 1; 
    Serial.println("Blood Hand Detected");
  }
  else if(LDR1Val > max1*70/100){
    s1 = 0;
    ss1 = -1;
    Serial.println("Hand Not Detected");
  }
  
  if(LDR2Val < max2*70/100){
    s2 = 1; 
    ss2 = 1;
    Serial.println("Blood Hand Detected");
  }
  else if(LDR2Val > max2*70/100){
    s2 = 0;
    ss2 = -1;
    Serial.println("Hand Not Detected");
  }
  
  if(LDR3Val < max3*70/100){
    s3 = 1; 
    ss3 = 1;
    Serial.println("Blood Hand Detected");
  }
  else if(LDR3Val > max3*70/100){
    s3 = 0;
    ss3 = -1;
    Serial.println("Hand Not Detected");
  }
  
  if(LDR4Val < max4*70/100){
    s4 = 1; 
    ss4 = 1;
    Serial.println("Blood Hand Detected");
  }
  else if(LDR4Val > max4*70/100){
    s1 = 0;
    ss1 = -1;
    Serial.println("Hand Not Detected");
  }

  int yy1 = ss1*(-4)+ss2*(-4)+ss3*(-4)+ss4*(-4);
  int yy2 = ss1*( 4)+ss2*( 4)+ss3*( 4)+ss4*( 4);
  
  if (yy1 == 16) riskLevel = 1;
  else if (yy1 >= yy2) riskLevel = 2;
  else if (yy2 > yy1) riskLevel = 3;
}

void readBP(){
  stepBP = flowBP/0.3497; //konversi dari flowrate ke step
  durationBP = durations*60*stepBP;//bpstep; //durasinya dikali step yang udah ml/menit

  if (i <= durationBP){ 
     i = pumpBP.currentPosition();  
     pumpBP.setSpeed(stepBP);
     pumpBP.runSpeed();
  }
}

void readSP(){
  stepSP = (flowSP / 0.0060240963855)/60; //dalam bentuk step/s
  dosageSP = volumeSP / 0.0060240963855;
  pumpSP.setSpeed(stepSP); 

  if (temp < volumeSP){ 
     stp = pumpSP.currentPosition();
     temp = stp * 0.0060240963855;  //0.003802;
     pumpSP.runSpeed();
  }
}

void Seq(){
  if (SR == 0){
    current_time = millis();
    if (VL4 == 1 && VL5 == 1 && VL6 == 0 && VL7 == 1 && VL8 == 0 && VL9 == 1 
    && VL10 == 1 && VL11 == 1 && SR == 0 && (millis() - currentMillis >= 5000)) {
      VL4  = 0; VL5  = 1; 
      VL6  = 1; VL7  = 1;
      VL8  = 1; VL9  = 1; 
      VL10 = 0; VL11 = 1;
      currentMillis = millis();
      SR = 1 ;
      mix();
    }
  } 

  if (SR == 1) {
    a = millis();
  }
  if (VL4 == 0 && VL5 == 1 && VL6 == 1 && VL7 == 1 && VL8 == 1 && VL9 == 1 
  && VL10 == 0 && VL11 == 1 &&  SR == 1 && a - currentMillis >= 20000) {
    VL4  = 1; VL5  = 1; 
    VL6  = 0; VL7  = 1;
    VL8  = 0; VL9  = 1; 
    VL10 = 1; VL11 = 1;
    currentMillis = millis();
    SR = 2;
    mix();
  }
  if (SR == 2) {
    b = millis();
  }
  if (VL4 == 1 && VL5 == 1 && VL6 == 0 && VL7 == 1  && VL8 == 0 && VL9 == 1 
  && VL10 == 1 && VL11 == 1 && SR == 2 && b - currentMillis >= 20000) {
    VL4  = 0; VL5  = 1; 
    VL6  = 1; VL7  = 1; 
    VL8  = 1; VL9  = 1; 
    VL10 = 0; VL10 = 1;
    currentMillis = millis();
    current_time = 0;
    SR = 1;
    mix();
  }
}

void valves(){
  if (VL4 == 0) digitalWrite(V4, LOW);
  else digitalWrite(V4, HIGH);
  
  if (VL5 == 0) digitalWrite(V5, LOW);
  else digitalWrite(V5, HIGH);

  if (VL6 == 0) digitalWrite(V6, LOW);
  else digitalWrite(V6, HIGH);

  if (VL7 == 0) digitalWrite(V7, LOW);
  else digitalWrite(V7, HIGH);

  if (VL8 == 0) digitalWrite(V8, LOW);
  else digitalWrite(V8, HIGH);
   
  if (VL9 == 0) digitalWrite(V9, LOW);
  else digitalWrite(V9, HIGH);
   
  if (VL10 == 0) digitalWrite(V10, LOW);
  else digitalWrite(V10, HIGH);
  
  if (VL11 == 0) digitalWrite(V11, LOW);
  else digitalWrite(V11, HIGH);
}

void bukaValve (){
  digitalWrite (V1,HIGH);
  digitalWrite (V2,HIGH);
  digitalWrite (V3,HIGH);
  digitalWrite (V4,HIGH);
  digitalWrite (V5,HIGH);
  digitalWrite (V6,HIGH);
  digitalWrite (V7,HIGH);
  digitalWrite (V8,HIGH);
  digitalWrite (V9,HIGH);
  digitalWrite (V10,HIGH);
  digitalWrite (V11,HIGH);
  digitalWrite (BYPASS1,HIGH);
  digitalWrite (BYPASS2,HIGH);
  digitalWrite (VDIAL,HIGH);
}

void persenTime (){
  static unsigned long duration = millis();
  if(millis()-duration>=(durations/100)*1000){  //Kenapa dibagi 100
    duration = millis();
    val=val+1;
    if (val==100) val=100;
  }
}

void bypassValve(){
  fuzzyBypass->setInput(1, T3Val);
  fuzzyBypass->setInput(2, ECVal);
  fuzzyBypass->setInput(3, PHVal);
  fuzzyBypass->fuzzify();

  float bypass = fuzzyBypass->defuzzify(1);

  if(bypass < 0.5 || bypassIN == 0){
    digitalWrite(BYPASS1, HIGH);
    digitalWrite(BYPASS2, LOW);
    digitalWrite(VDIAL, HIGH);
    VL12 = 0;
    VL13 = 1;
  }
  else if(bypass >= 0.5 || bypassIN == 1){
    digitalWrite(BYPASS1, LOW);
    digitalWrite(BYPASS2, HIGH);
    digitalWrite(VDIAL, LOW);
    VL12 = 1;
    VL13 = 0;
  }
}

void speedP5(){
  fuzzyPump->setInput(1,flowRate);
  fuzzyPump->fuzzify();

  int valuePWM = fuzzyPump->defuzzify(1);
  
  if (valuePWM>=260 && valuePWM<=280) cf=81;
  else if(valuePWM<260 && valuePWM>=250) cf=78;
  else if(valuePWM>=230 && valuePWM<250) cf=77;
  else if(valuePWM>=220 && valuePWM<230) cf=75;
  else if(valuePWM>=210 && valuePWM<220) cf=74;
  else if(valuePWM>=190 && valuePWM<210) cf=72;
  else if(valuePWM>=180 && valuePWM<190) cf=69;
  else if(valuePWM>=170 && valuePWM<180) cf=66;
  else if(valuePWM>=160 && valuePWM<170) cf=63;
  analogWrite(P5,valuePWM);
}

void pulseCounter(){
  pulseCount++;
}

void BLD(){
  digitalWrite(BLD2, LOW);
  digitalWrite(BLD3, LOW);
  int redFrequency = map(pulseIn(BLD_OUT, HIGH), 3262, 1544, 95, 255);

  digitalWrite(BLD2, HIGH);
  digitalWrite(BLD3, HIGH);
  int greenFrequency = map(pulseIn(BLD_OUT, HIGH), 7539, 1878, 0, 110);

  digitalWrite(BLD2, LOW);
  digitalWrite(BLD3, HIGH);
  int blueFrequency = map(pulseIn(BLD_OUT, HIGH), 5656, 1544, 40, 50);

  fuzzyBLD->setInput(1, abs(redFrequency));
  fuzzyBLD->setInput(2, abs(greenFrequency));
  fuzzyBLD->setInput(3, abs(blueFrequency));
  fuzzyBLD->fuzzify();

  int detection = fuzzyBLD->defuzzify(1);

  if(detection >= 50) BD = 3;
  else BD = 1;
}
