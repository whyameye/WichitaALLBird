import serial, time, sys, select, serial.tools.list_ports
from itertools import chain


# ser = serial.Serial('/dev/cu.wchusbserial14120', 115200)
ser = serial.Serial('/dev/ttyUSB0', 115200)

def printPorts():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}".format(port))


def getInput(timeToWait):
    i, o, e = select.select( [sys.stdin], [], [], timeToWait )
    if (i):
        print(sys.stdin.readline().strip())
        return True
    return False
    
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


def testStrand():
    while True:
        print()
        print("Ports available: ")
        printPorts()
        port = input("Port #: ")
        ser = serial.Serial('/dev/ttyUSB'+port, 115200)
        arduinoID = 1 # TODO
        while True:
            print("Port "+port+" corresponds to Arduino ID "+str(arduinoID))
            strand = input("Strand ('<ENTER>' to reenter port): ")
            if strand == "":
                ser.close()
                break
            print("Flashing Arduino ID "+str(arduinoID)+" strand "+strand+". <ENTER> to stop.")
            strand = int(strand)
            while True:
                for i in range(5):
                    setLED(strand, i, 150, 254)
                    time.sleep(.001)
                time.sleep(1)
                for i in range(5):
                    setLED(strand,i, 150, 0)
                    time.sleep(.001)
                if getInput(1):
                    break



