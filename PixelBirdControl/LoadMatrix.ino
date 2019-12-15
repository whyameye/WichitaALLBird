// Matrix managment functions

void clearMatrix(){
  for(uint8_t i=0;i< BitsPerStrand;i++){
    blockB[i] = 0;
    blockC[i] = 0;
    blockD[i] = 0;
  }
}

// 
void setBirdColorBrightness(uint8_t strandBird, uint8_t color, uint8_t brightness){
  uint8_t strand = (strandBird & 0xF8)/8;  // number from 0 to 17 (18 to 32 not used)
  strand = constrain(strand,0,17);  
  uint8_t bird = (strandBird & 0x07) * 32;   // number from 0 to 4(now 5) (6 to 7 not used) *32 bits per bird  
  bird = constrain(bird,0,BitsPerStrand);
  uint32_t birdColor = Wheel(color,brightness);
  uint8_t Bbit;

  if(strand > 11){
    Bbit = (strand - 10);
    for(uint8_t i = 0;i < 32; i++){
      bitWrite(blockD[bird+i],Bbit,bitRead(birdColor,(31-i)));
    }
    return;
  }
  if(strand > 5){
    Bbit = strand - 6;
    for(uint8_t i = 0;i < 32; i++){
      bitWrite(blockC[bird+i],Bbit,bitRead(birdColor,(31-i)));
    }
    return;
  }
  Bbit = strand;
  for(uint8_t i = 0;i < 32; i++){
    bitWrite(blockB[bird+i],Bbit,bitRead(birdColor,(31-i)));
  }
  return;
}

uint32_t colorPicker(uint8_t rgbw, uint8_t lux){
  if (rgbw == 0) return (lux * 0x1000000);
  if (rgbw == 1) return (lux * 0x10000);
  if (rgbw == 2) return (lux * 0x100);
  if (rgbw == 3) return (lux * 0x1);
  return 0;
    }

uint32_t fader(uint8_t r, uint8_t g, uint8_t b, uint8_t w, uint8_t lux){
  uint32_t randomColor = 0;
  if(w==1)randomColor = w * lux;
  randomColor = randomColor + b * (lux*0x100);
  randomColor = randomColor + r * (lux *0x10000);
  randomColor = randomColor + g * (lux *0x1000000);
  return randomColor;
}
