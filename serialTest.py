import serial, time
from itertools import chain

# ser = serial.Serial('/dev/cu.usbserial-14120', 115200)
ser = serial.Serial('/dev/cu.wchusbserial14120', 115200)

def setLED(strand, numOnStrand, color, amplitude):
    bytes = []
    bytes.append((strand << 3) + numOnStrand)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xff)
    ser.write(serial.to_bytes(bytes))

def test1(amp):
    for color in range(254):
        for strand in range(18):
            for num in range(5):
                setLED(strand, num, color, amp)
                time.sleep(.001)

def test2(color):
    for amp in chain(range(128),range(128,0,-1)):
        for strand in range(18):
            for num in range(5):
                setLED(strand, num, color, amp)
                time.sleep(.001)
