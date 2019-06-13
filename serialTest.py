import serial, time, sys, select, serial.tools.list_ports, binascii, os
from itertools import chain
BAUDRATE = 9600

# ser = serial.Serial('/dev/cu.wchusbserial14120', 115200)
# ser = serial.Serial('/dev/ttyUSB1', 115200)

def resetArduino(port):
    os.system("./dtr "+port)
    
def printPorts():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}".format(port))

def choosePort():
    print()
    print("Ports available: ")
    printPorts()
    port = input("Port #: ")
    return port

def getInput(timeToWait):
    i, o, e = select.select( [sys.stdin], [], [], timeToWait )
    if (i):
        print(sys.stdin.readline().strip())
        return True
    return False
    
def setLED(ser, strand, numOnStrand, color, amplitude):
    bytes = []
    bytes.append((strand << 3) + numOnStrand)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xff)
    ser.write(serial.to_bytes(bytes))

def test1(amp):
    port = choosePort()
    ser = serial.Serial('/dev/ttyUSB'+port, BAUDRATE)
    for color in range(254):
        for strand in range(18):
            for num in range(5):
                setLED(ser, strand, num, color, amp)
                time.sleep(.001)

def test2(color):
    port = choosePort();
    ser = serial.Serial('/dev/ttyUSB'+port, BAUDRATE)
    for amp in chain(range(0,128,1),range(128,0,-1)):
        for strand in range(18):
            for num in range(5):
                setLED(ser, strand, num, color, amp)
                time.sleep(.001)

def testStrand():
    while True:
        port = choosePort();
        # ser = serial.Serial('/dev/ttyUSB'+port, 115200)
        ser = serial.Serial('/dev/ttyUSB'+port, BAUDRATE)
        arduinoID = getID(ser)
        while True:
            print("Port "+port+" corresponds to Arduino ID "+str(arduinoID))
            strand = input("Strand ('<ENTER>' to reenter port): ")
            if strand == "":
                ser.close()
                break
            print("Flashing Arduino ID "+str(arduinoID)+" strand "+strand+". <ENTER> to stop.")
            strand = int(strand)
            while True:
                for i in range(6):
                    setLED(ser, strand, i, 150, 254)
                    time.sleep(.001)
                time.sleep(0.25)
                for i in range(6):
                    setLED(ser, strand,i, 150, 0)
                    time.sleep(.001)
                if getInput(0.25):
                    break

def getID(ser):
    bytes = []
    bytes.append(0xff)
    bytes.append(0xff)
    ser.write(serial.to_bytes(bytes))
    # time.sleep(.01)
    time.sleep(1)
    msg = ser.read(ser.inWaiting())
    return msg[0]
