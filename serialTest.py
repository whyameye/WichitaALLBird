import serial, time, sys, select, serial.tools.list_ports, binascii, os
from itertools import chain
import random
BAUDRATE = 921600

# ser = serial.Serial('/dev/cu.wchusbserial14120', 115200)
# ser = serial.Serial('/dev/ttyUSB1', 115200)

def resetArduino(port):
    # must call 2x for some unknown reason
    os.system("./dtr "+port)
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

def openPort():
    port = choosePort();
    resetArduino("/dev/ttyUSB"+port)
    ser = serial.Serial('/dev/ttyUSB'+port, BAUDRATE)
    ser.dtr = False
    ser.rts = False
    time.sleep(.1)
    while ser.in_waiting:  # Or: while ser.inWaiting():
        ser.readline()
    time.sleep(.1)
    print("ID : {} ".format(getID(ser)))
    time.sleep(1)
    return ser

def closePort(ser):
    ser.close()
    
def getInput(timeToWait):
    i, o, e = select.select( [sys.stdin], [], [], timeToWait )
    if (i):
        print(sys.stdin.readline().strip())
        return True
    return False
    
def setLED(ser, numOnStrand, color, amplitude):
    bytes = []
    bytes.append(numOnStrand >> 8)
    bytes.append(numOnStrand & 0xff)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xFF)
    ser.write(serial.to_bytes(bytes))
    ser.flush()
    # time.sleep(.1)
    # while ser.in_waiting:  # Or: while ser.inWaiting():
    #    print(ser.readline())
    
              
def test1(amp):
    """cycle all colors with constant amplitude
    Parameter:
    __________
    amplitude : range (0 - 254)
                ranges above 127 add white LED
    """
    ser = openPort()
    test1do(ser, amp)
    
def test1do(ser, amp):
    for color in range(0,255,1):
        print("\r>> Color (0-254): {}  ".format(color), end='')
        for strand in range(0,18):
            for num in range(5):
                setLED(ser, strand, num, color, amp)
                time.sleep(.0006)
        # time.sleep(.5)
    test1do(ser, amp)
    
def test2(color):
    """cycle one color from amplitude 0 - 127 and back
    Parameter:
    ----------
    color : range 0 - 254
    """
    ser = openPort();
    test2do(ser,color)
    
def test2do(ser,color):
    for amp in chain(range(10,128,1),range(127,9,-1)):
        print("\r>> Amplitude (0-127): {}  ".format(amp), end='')
        for strand in range(18):
            for num in range(5):
                setLED(ser, strand, num, color, amp)
                time.sleep(.0006)
    test2do(ser,color)

def testStrand():
    """flash prompted strand white
    """

    while True:
        port = choosePort();
        ser = serial.Serial('/dev/ttyUSB'+port, BAUDRATE)
        # ser = serial.Serial('/dev/ttyACM'+port, BAUDRATE)
        ser.dtr = False
        ser.rts = False
        time.sleep(.1)
        while ser.in_waiting:  # Or: while ser.inWaiting():
            ser.read()
        arduinoID = getID(ser)
        print("Port "+port+" corresponds to Arduino ID "+str(arduinoID))
        print("Flashing Arduino ID "+str(arduinoID)+". <ENTER> to stop.")
        while True:
            x = random.randrange(255);
            for i in range(190):
                # print("sending: %d, 150, 254" % (i))
                setLED(ser, i, x, 150)
                # time.sleep(.003)
                #while ser.in_waiting:  # Or: while ser.inWaiting():
                #    print(ser.readline())

            # print()
            time.sleep(0.25)
            for i in range(190):
                # print("sending: %d, 150, 0" % (i))
                setLED(ser, i, 0,0)
                # time.sleep(.003)
                # while ser.in_waiting:  # Or: while ser.inWaiting():
                #    ser.readline()

            if getInput(0.25):
                break
def testStrands(port, times):
    """flash all strands (0-17) white
    Parameters
    ----------
    port  : number corresponding to which /dev/ttyUSB port is being used
    times : number of times to flash strang
    """
    if True:
    # for port in range(9):
        ser = serial.Serial('/dev/ttyUSB'+str(port), BAUDRATE)
        arduinoID = 13
        while arduinoID > 12:
            arduinoID = getID(ser)
        print("Port "+str(port)+" corresponds to Arduino ID "+str(arduinoID))
        # time.sleep(10);
        for strand in range(18):
            print("Flashing Arduino ID "+str(arduinoID)+" strand "+str(strand))
            for j in range(times):
                for i in range(6):
                    setLED(ser, strand, i, 150, 254)
                    time.sleep(.1)
                time.sleep(0.25)
                for i in range(6):
                    setLED(ser, strand,i, 150, 0)
                    time.sleep(.1)
                time.sleep(0.25)
        ser.close()


def getID(ser):
    msg = ""
    ans = 9
    print("trying to read ID")
    bytes = []
    bytes.append(0xFF)
    bytes.append(0xFF)
    while ans > 8:
        ser.write(serial.to_bytes(bytes))
        ser.flush()
        time.sleep(.1)
        msg = ser.read(ser.inWaiting())
        try:
            ans = msg[0]
        except:
            ans = 9
    return ans
