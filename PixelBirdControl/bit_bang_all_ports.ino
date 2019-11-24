// Actually send the next set of 8 WS2812B encoded bits to the 8 pins.
// We must to drop to asm to enusre that the complier does
// not reorder things and make it so the delay happens in the wrong place.
static inline __attribute__ ((always_inline)) void sendBitX8( uint8_t Bbits, uint8_t Cbits, uint8_t Dbits ) {

    const uint8_t onBits = 0xff;          // We need to send all bits on on all pins as the first 1/3 of the encoded bits
    asm volatile (
      "out %[portB], %[onBits] \n\t"           // 1st step - send T0H high 
      "out %[portC], %[onBits] \n\t"           // 1st step - send T0H high 
      "out %[portD], %[onBits] \n\t"           // 1st step - send T0H high 
      ".rept %[T0HCycles] \n\t"               // Execute NOPs to delay exactly the specified number of cycles
        "nop \n\t"
      ".endr \n\t"
      "out %[portB], %[Bbits] \n\t"             // set the output bits to thier values for T0H-T1H
      "out %[portC], %[Cbits] \n\t"             // set the output bits to thier values for T0H-T1H
      "out %[portD], %[Dbits] \n\t"             // set the output bits to thier values for T0H-T1H
      ".rept %[dataCycles] \n\t"               // Execute NOPs to delay exactly the specified number of cycles
      "nop \n\t"
      ".endr \n\t"
      "out %[portB],__zero_reg__  \n\t"        // last step - T1L all bits low
      "out %[portC],__zero_reg__  \n\t"        // last step - T1L all bits low
      "out %[portD],__zero_reg__  \n\t"        // last step - T1L all bits low
      // Don't need an explicit delay here since the overhead that follows will always be long enough
      ::
      [portB]    "I" (_SFR_IO_ADDR(PIXEL_PORTB)),
      [portC]    "I" (_SFR_IO_ADDR(PIXEL_PORTC)),
      [portD]    "I" (_SFR_IO_ADDR(PIXEL_PORTD)),
      [Bbits]   "d" (Bbits),
      [Cbits]   "d" (Cbits),
      [Dbits]   "d" (Dbits),
      [onBits]   "d" (onBits),
      [T0HCycles]  "I" (NS_TO_CYCLES(T0H) - 2),           // 1-bit width less overhead  for the actual bit setting, note that this delay could be longer and everything would still work
      [dataCycles]   "I" (NS_TO_CYCLES((T1H-T0H)) - 2)     // Minimum interbit delay. Note that we probably don't need this at all since the loop overhead will be enough, but here for correctness
    );
}  
static inline void __attribute__ ((always_inline)) sendPixelbank() {
  cli();
  for(uint8_t i=0;i< BitsPerStrand;i++){
    sendBitX8(blockB[i],blockC[i],blockD[i]);
  }
  sei();
}

static inline void __attribute__ ((always_inline)) sendRandomPixelbank( uint32_t randomColor, uint8_t row, uint8_t bank0, uint8_t bank1, uint8_t bank2 ) {

uint8_t bit = 0;

  cli();
  bit=32;       
  while (bit--) {
     if(bitRead(randomColor,bit)){
      blockB[bit] = bank0;
      blockC[bit] = bank0;
      blockD[bit] = bank0;
     }else{
      blockB[bit] = 0;
      blockC[bit] = 0;
      blockD[bit] = 0;
     }
  }
  for(int i = 0;i < 5;i++){
    if(bitRead(row, i)){
      bit=32;       
      while (bit--) {
        sendBitX8( blockB[bit],blockC[bit],blockD[bit] );    
      }
    }else{
        bit=32;       
        while (bit--) {
           sendBitX8( 0,0,0 );    
        }
    }
  }
  sei();
}

    
