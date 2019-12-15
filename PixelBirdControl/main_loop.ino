void setup() {
  randomSeed(analogRead(0));
  PIXEL_DDRB = 0xff;    // Set all bank pins to output 
  PIXEL_DDRC = 0xff;    // Set all bank pins to output 
  PIXEL_DDRD = 0xff;    // Set all bank pins to output 
  Serial.begin(115200);
  //Serial.print("Board ID: ");
  StrandServerID = (getID());
  //Serial.println(StrandServerID,DEC);
  // if(debug) Serial.println("bird , color , brightness ");
  
   sendPixelbank();  // in the bit_bang_all_ports tab
   delay(500);
   clearMatrix();  //in the LoadMatrix tab
   delay(1000);
   sendPixelbank();  // in the bit_bang_all_ports tab
}

void Xdelay(int X){
  int i=0;
  while(X > i++){
    delay(1);
    if(Serial.available())return;
  }
}
  
void randomPixel() {
  uint8_t pColor = random(4);  // if you just want RGBW
//  uint8_t rColor = random(20,(brite/64));  //this is an attempt to cover the full range of colors
//  uint8_t gColor = random(20,brite);   //
//  uint8_t bColor = random(20,brite);   // 
//  uint8_t wColor = random(20,brite);   //
  uint8_t bird = 0;
  bitSet (bird,random(4));
//  bitSet (bird,random(4));
  uint8_t PortB = 0;
  uint8_t PortC = 0;
  uint8_t PortD = 0;
  for(int i = 0;i < density;i++){
    randomStrand = random(18);
    if(randomStrand < 6)bitSet(PortB,randomStrand);
    if((randomStrand >5)&&(randomStrand < 12))bitSet(PortC,(randomStrand-6));
    if((randomStrand >11)&&(randomStrand < 18))bitSet(PortD,(randomStrand-10));
  }  

  for(int x=0;x<brite;x++){
//    randomColor = fader(rColor,gColor,bColor,wColor,x);
    randomColor = colorPicker(pColor,x);
    sendRandomPixelbank( randomColor,bird,PortB,PortC,PortD);  // in the bit_bang_all_ports tab
    Xdelay(spd/10);
  }
  Xdelay(spd*5);  //  hold on at full brite
  for(int x=brite;x>-1;x--){
//    randomColor = fader(rColor,gColor,bColor,wColor,x);
    randomColor = colorPicker(pColor,x);
    sendRandomPixelbank( randomColor,bird,PortB,PortC,PortD);  // in the bit_bang_all_ports tab
    Xdelay(spd/10);
  }
  Xdelay(spd);  //pause before looping
  if(Serial.available()){
    timeoutMillis = millis()+WaitIThoughtIHeardSomething;
    clearMatrix();  //in the LoadMatrix tab
//    delay(1000);
//    sendPixelbank();  // in the bit_bang_all_ports tab
  }
}

// -------------------------------- The loop ------------------------------------
void loop() {
    //wdt_reset();   // pet the watch dog to make him happy
    //look for incoming bytes and exicute something if return is true
     if (comm){ 
      comm = false;
      setBirdColorBrightness(SerialQue[2],SerialQue[1],SerialQue[0]);
      sendPixelbank();
      timeoutMillis = millis()+WaitIThoughtIHeardSomething;
     }
  currentMillis = millis();
  if (currentMillis > timeoutMillis) {
    timeoutMillis = 0;
    randomPixel();        // do the random pattern until we see a serial input
    // Serial.println("loop");
  }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    uint8_t inByte;
    
      inByte = Serial.read();     // get incoming byte:
       //Serial.write(inByte);
      if (inByte == 0xff) {
        switch (SerialQueCnt) {
        case 0:
    Serial.write(StrandServerID); // if two FFs are received send the Strand Server ID
    return;
        case 3:
    SerialQueCnt = 0;
    comm = true;
    return;
        default:
    SerialQueCnt = 0;
    return;
        }
      }
      SerialQue[2]=SerialQue[1];
      SerialQue[1]=SerialQue[0];
      SerialQue[0]=inByte;
      SerialQueCnt = (++SerialQueCnt % 4);
    }
    return;
  }
    
