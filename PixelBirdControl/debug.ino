void data_dump() {
  Serial.write(SerialQue[0]);
  Serial.write(SerialQue[1]);
  Serial.write(SerialQue[2]);
}

void printMatrix(){   //data dump of the arrays that hold the port matrix of data
  for (uint8_t i=0;i<8;i++){   
    for(uint8_t j=0;j<160;j++){
        Serial.write(bitRead(blockB[j],i));
    }
//    Serial.println("");
    Serial.write(0xff);
  }
  for (uint8_t i=0;i<8;i++){   
    for(uint8_t j=0;j<160;j++){
        Serial.write(bitRead(blockC[j],i));
    }
//    Serial.println("");
  }
  for (uint8_t i=0;i<8;i++){   
    for(uint8_t j=0;j<160;j++){
        Serial.write(bitRead(blockD[j],i));
    }
//    Serial.println("");
    Serial.write(0xff);
  }
//    Serial.println("");
    Serial.write(0xff);
}

void ScrollColors(){
  int k;
    for(int j = 0;j<255;j++){
      for(int i = 0;i<145;i+=3){
        k = i+j;
        if(k > 255) k=k-255;
        setBirdColorBrightness(i,k,40);
        sendPixelbank();
  //    delay(1);
      }
    }     
    for(int j = 40;j > 0;j--){
      for(int i = 0;i<145;i+=3){
        setBirdColorBrightness(i,i,j);
        sendPixelbank();
        delay(1);
    }
  }
}

void SetRedMatrix(){
  uint8_t mask = 0x04;  // the third bit
  for (uint8_t i=0;i<MaxBirdsPerStrand;i++){   //three lights per strand at first
      blockB[(i*32)+7]=0xff;
      blockC[(i*32)+30]=0xff;
      blockD[(i*32)+15]=0xff;
  }
}

void testColorPack(){
  for(byte i = 0;i<255;i++){
    Serial.println(Wheel(i,10));
  }
}
