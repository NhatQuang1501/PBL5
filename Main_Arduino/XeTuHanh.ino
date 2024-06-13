
#define enA 10//Enable1 L298 Pin enA 
#define in1 9 //Motor1  L298 Pin in1 
#define in2 8 //Motor1  L298 Pin in1 
#define in3 7 //Motor2  L298 Pin in1 
#define in4 6 //Motor2  L298 Pin in1 
#define enB 5 //Enable2 L298 Pin enB 

#define L_S A0
#define R_S A1

#define echo A2   
#define trigger A3 

#define lightSensor A4 

#define servo A5

int Set=12;
int speed_nm = 120;
int speed_RL = 230;
int distance_L, distance_F, distance_R; 
int currentStop;
int ledToStop;


void setup(){

Serial.begin(9600);

pinMode(R_S, INPUT);
pinMode(L_S, INPUT);

pinMode(echo, INPUT );
pinMode(trigger, OUTPUT);  

pinMode(enA, OUTPUT);
pinMode(in1, OUTPUT);
pinMode(in2, OUTPUT);
pinMode(in3, OUTPUT);
pinMode(in4, OUTPUT);
pinMode(enB, OUTPUT);

analogWrite(enA, speed_nm);
analogWrite(enB, speed_nm);

pinMode(servo, OUTPUT);
pinMode(lightSensor, INPUT);

 for (int angle = 70; angle <= 140; angle += 5)  {
   servoPulse(servo, angle);  }
 for (int angle = 140; angle >= 0; angle -= 5)  {
   servoPulse(servo, angle);  }

 for (int angle = 0; angle <= 70; angle += 5)  {
   servoPulse(servo, angle);  }

distance_F = Ultrasonic_read();

delay(500);
}


void loop(){  
//==============================================
//     Line Follower and Obstacle Avoiding
//==============================================  

distance_F = Ultrasonic_read();


 if((digitalRead(R_S) == 0)&&(digitalRead(L_S) == 0)){
        if(distance_F > Set){forword();
        }
        else if(digitalRead(lightSensor) == 0){
          Stop();
        }
        else{
          Check_side();
        }  
 }  
 
//if Right Sensor is Black and Left Sensor is White then it will call turn Right function
else if((digitalRead(R_S) == 1)&&(digitalRead(L_S) == 0)){turnRight();}  

//if Right Sensor is White and Left Sensor is Black then it will call turn Left function
else if((digitalRead(R_S) == 0)&&(digitalRead(L_S) == 1)){turnLeft();} 

  if (digitalRead(lightSensor) == 0) {
    Stop();
  }
    
delay(10);
}

void servoPulse (int pin, int angle){
int pwm = (angle*11) + 500;
 digitalWrite(pin, HIGH);
 delayMicroseconds(pwm);
 digitalWrite(pin, LOW);
 delay(50);
}


//**********************Ultrasonic_read****************************
long Ultrasonic_read(){
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  long time = pulseIn (echo, HIGH);
  return time / 29 / 2;
}

void compareDistance(){

  if(distance_L < distance_R){
  backword();
  delay(80);
  turnLeft_();
  delay(270);
  forword();
  delay(800);
  turnRight_();
  delay(370);
  forword();
  if((digitalRead(L_S) == 1)&&(digitalRead(R_S) == 0)){
    turnLeft_();
    } 
  if((digitalRead(R_S) == 1)&&(digitalRead(L_S) == 0)){
    turnLeft_();
    delay(400);
    } 


  }
  if(distance_R < distance_L){
  backword();
  delay(80);
  turnRight_();
  delay(270);
  forword();
  delay(800);
  turnLeft_();
  delay(370);
  forword();
  if((digitalRead(R_S) == 1)&&(digitalRead(L_S) == 0)){
    turnRight_();
    }
  if((digitalRead(L_S) == 1)&&(digitalRead(R_S) == 0)){
    turnRight_();
    delay(400);
    }  

  }

}

void Check_side(){
    Stop();
    delay(100);
 for (int angle = 70; angle <= 140; angle += 5)  {
   servoPulse(servo, angle);  }
    delay(300);
    distance_R = Ultrasonic_read();
//    Serial.print("D R=");Serial.println(distance_R);
    delay(100);
  for (int angle = 140; angle >= 0; angle -= 5)  {
   servoPulse(servo, angle);  }
    delay(500);
    distance_L = Ultrasonic_read();
//    Serial.print("D L=");Serial.println(distance_L);
    delay(100);
 for (int angle = 0; angle <= 70; angle += 5)  {
   servoPulse(servo, angle);  }
    delay(300);
    if(distance_R >=10 || distance_L >=10){
    compareDistance();
    }
}
//A la dc phai, B la dc trai
// dc trai < dc phai
void forword(){ 
analogWrite(enA, speed_nm);  
analogWrite(enB, speed_nm+15);
digitalWrite(in1, HIGH);
digitalWrite(in2, LOW);
digitalWrite(in3, HIGH);
digitalWrite(in4, LOW);
}

void backword(){
analogWrite(enA, speed_nm+10);  
analogWrite(enB, speed_nm+25);
digitalWrite(in1, LOW);
digitalWrite(in2, HIGH); 
digitalWrite(in3, LOW);
digitalWrite(in4, HIGH);

}

void turnRight(){ 
analogWrite(enA, speed_RL);  
analogWrite(enB, speed_RL+15);
digitalWrite(in1, LOW);
digitalWrite(in2, HIGH);
digitalWrite(in3, HIGH);
digitalWrite(in4, LOW);

delay(10);
analogWrite(enA, speed_nm);  
analogWrite(enB, speed_nm+15);
}

void turnLeft(){ 
analogWrite(enA, speed_RL);  
analogWrite(enB, speed_RL+15);
digitalWrite(in1, HIGH);
digitalWrite(in2, LOW);
digitalWrite(in3, LOW);
digitalWrite(in4, HIGH);

delay(10);
analogWrite(enA, speed_nm);  
analogWrite(enB, speed_nm+15);
}

void Stop(){
digitalWrite(in1, LOW);
digitalWrite(in2, LOW);
digitalWrite(in3, LOW);
digitalWrite(in4, LOW);
}

void turnRight_(){ 
analogWrite(enA, 255);  
analogWrite(enB, 255);
digitalWrite(in1, LOW);
digitalWrite(in2, HIGH);
digitalWrite(in3, HIGH);
digitalWrite(in4, LOW);
}

void turnLeft_(){ 
analogWrite(enA, 255);  
analogWrite(enB, 255);
digitalWrite(in1, HIGH);
digitalWrite(in2, LOW);
digitalWrite(in3, LOW);
digitalWrite(in4, HIGH);

}