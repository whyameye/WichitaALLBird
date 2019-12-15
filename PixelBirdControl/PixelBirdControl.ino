
// The main goal of this program is to receive data packets from the 
// Advanced Learning Center Avian Migration sculpture main computor and control several strands of birds
// 
// (this)PixelBirdControl module holds all the constants, declarations, setups, and initializations for the arduino
// [Tabs]
// bit bang/ is the function that sends the data out to the strands
// comm/ handles all the serial communication stuff
// debug/ is a bunch of print statments
// main_loop/ is the executive

/* 
 *  Protocol from main computer to Arduino:
    byte 1: strand/number on strand
    strand is top 5 bits with range (0-17)
    # on strand is bottom 3 bits with range (0-4)
    byte 2: color (0-254)
    byte 3: amplitude (0-254) may include brightness and hue(addition of whiteness)
    byte 4: “end:” 0xFF
 */
//#include <avr/wdt.h>

// RandomPixelVariables---
const int spd = 200;
const int density = 5;
const uint8_t brite = 0x40;
uint8_t randomStrand = 0;
uint32_t randomColor;

//BirdControlVariables
const unsigned long WaitIThoughtIHeardSomething = 10000;  // stop random for X milliseconds and listen for instructions
unsigned long timeoutMillis = 0;
unsigned long currentMillis = millis();
bool comm = false; 
const uint8_t MaxBirdsPerStrand = 6; 
const uint8_t BitsPerStrand = MaxBirdsPerStrand * 32; 
uint8_t StrandServerID = 255; // this will be set in initialization
const int debug = 0;
uint8_t SerialQue[5];
uint8_t SerialQueCnt = 0;
uint8_t strand = 0;
uint32_t color = 0;
uint8_t blockB[BitsPerStrand]; // this block of data will hold all the bits for a port so they can be streamed out real fast
uint8_t blockC[BitsPerStrand]; // this block of data will hold all the bits for a port so they can be streamed out real fast
uint8_t blockD[BitsPerStrand]; // this block of data will hold all the bits for a port so they can be streamed out real fast

#define PIXEL_PORTB  PORTB  // Port of the pin the pixels are connected to
#define PIXEL_PORTC  PORTC  // Port of the pin the pixels are connected to
#define PIXEL_PORTD  PORTD  // Port of the pin the pixels are connected to
#define PIXEL_DDRB   DDRB   // Port of the pin the pixels are connected to
#define PIXEL_DDRC   DDRC   // Port of the pin the pixels are connected to
#define PIXEL_DDRD   DDRD   // Port of the pin the pixels are connected to

// These are the timing constraints taken mostly from the WS2812 datasheets
#define T1H  900    // Width of a 1 bit in ns
#define T1L  600    // Width of a 1 bit in ns
#define T0H  400    // Width of a 0 bit in ns
#define T0L  900    // Width of a 0 bit in ns
#define RES 6000    // Width of the low gap between bits to cause a frame to latch

// Here are some convience defines for using nanoseconds specs to generate actual CPU delays
#define NS_PER_SEC (1000000000L)          // Note that this has to be SIGNED since we want to be able to check for negative values of derivatives
#define CYCLES_PER_SEC (F_CPU)
#define NS_PER_CYCLE ( NS_PER_SEC / CYCLES_PER_SEC )
#define NS_TO_CYCLES(n) ( (n) / NS_PER_CYCLE )


// pack up the rgbw values into one big word
uint32_t colorPack(uint32_t red, uint32_t green, uint32_t blue, uint32_t white) {
  return (green << 24)+(red << 16)+(blue << 8)+white;
}

// Input a value 0 to 255 for color and a value 0 to 255 for brightness.
// The colours are a transition r - g - b - back to g.
uint32_t Wheel(uint32_t WheelPos , uint32_t brightness) {
  uint32_t plusTone;
  uint32_t minusTone;
  uint32_t whitness = 0;
    if(brightness > 128) whitness = brightness -128;
      if(debug)Serial.println(brightness,BIN);
      if(debug)Serial.println(whitness,BIN);
  if(WheelPos < 85) {
    plusTone = (WheelPos *3*brightness) >> 8;
    minusTone = ((255-(WheelPos *3))*brightness) >> 8;
//    whitness = (brightness && 0xF0) >> 4;
//    if(debug)Serial.print(plusTone,DEC);
//    if(debug)Serial.println(minusTone,DEC);
    return colorPack(minusTone, plusTone,0,whitness);
    }
  if(WheelPos < 170) {
    WheelPos -= 85;
    plusTone = (WheelPos *3*brightness) >> 8;
    minusTone = ((255-(WheelPos *3))*brightness) >> 8;
//    if(debug)Serial.println(plusTone,DEC);
//    if(debug)Serial.println(minusTone,DEC);
      return colorPack(0,minusTone,plusTone,whitness);
  }
  WheelPos -= 170;
    plusTone = (WheelPos *3*brightness) >> 8;
    minusTone = ((255-(WheelPos *3))*brightness) >> 8;
//    if(debug)Serial.println(plusTone,DEC);
//    if(debug)Serial.println(minusTone,DEC);
      return colorPack(plusTone,0,minusTone,whitness);
}

// each strand server circuit board has a resistor divider that sets a voltage on A6 
// to determine which strands is is acting on / convert =ToQuadrame1 works with getID
uint8_t convertToQuadramel(uint16_t val) {
  if (val < 200) return 0;
  if (val < 512) return 1;
  if (val < 924) return 2;
  return 3;
}
uint8_t getID() {
  return convertToQuadramel(analogRead(A6)) * 4 + convertToQuadramel(analogRead(A7));
}
