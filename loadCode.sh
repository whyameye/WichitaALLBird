#!/bin/bash
if [ "X$1" = "X" ] || [ "X$2" = "X" ]; then
    echo "Usage: $0 port# filename"
    exit 0
fi
if [ ! -f $2 ]; then
    echo "file $1 not found"
   exit 0
fi  
/home/bird/dev/arduino-PR-beta1.9-BUILD-78/hardware/tools/avr/bin/avrdude -C/home/bird/dev/arduino-PR-beta1.9-BUILD-78/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -P/dev/ttyUSB$1 -b57600 -D -Uflash:w:$2:i
