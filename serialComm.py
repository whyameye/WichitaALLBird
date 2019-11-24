import serial, threading, time, os
from common import *

serverIdPortDict = {}
ports = []
BAUDRATE = 115200
serverThreads = []
serverLedLists=[]


def initializeServerLedLists():
    """serverLedLists is an array of arrays with each index to the parent array representing a server ID
    The child arrays are lists of LEDs to change of the form [<strand>, <numOnStrand>, <color>, <amplitude>]
    strand: json of entire description of strand
    numOnStrand: uint8
    color: uint8
    amplitude: uint8
    """
    global serverLedLists
    
    serverLedLists = []
    for i in range(NUMBER_OF_SERVERS):
        serverLedLists.append([])

def addToServerLedLists(serverToAssign, strandOnServer, numOnStrand, color, amp):
    serverLedLists[serverToAssign].append([strandOnServer, numOnStrand, color, amp])
    
def resetArduino(port):
    # must call 2x for some unknown reason
    os.system("./dtr "+port)
    time.sleep(2.25)
    # os.system("./dtr "+port)

def getID(ser):
    ans = chr(10)
    while ord(ans) > 9:
        debug("trying to read ID")
        msg = ""    
        bytes = []
        bytes.append(0xff)
        bytes.append(0xff)
        ser.write(serial.to_bytes(bytes))
        time.sleep(.01)
        msg = ser.read(ser.inWaiting())
        try: 
            ans = msg[0]
        except:
            ans = chr(10)
            time.sleep(.5)
    return ans

def begin(numOfServers = NUMBER_OF_SERVERS):
    '''create arduinoID -> port dictionary
    open ports
    '''
    global serverIdPortDict
    
    if DRY_RUN:
        for i in range(numOfServers):
            serverIdPortDict[i] = i
        return
    
    for i in range(numOfServers):
        resetArduino("/dev/ttyUSB"+str(i))
        ports.append(serial.Serial("/dev/ttyUSB"+str(i), BAUDRATE))
        serverIdPortDict[ord(getID(ports[i]))] = i

def setLED(ser, strand, numOnStrand, color, amplitude):
    bytes = []
    bytes.append((strand << 3) + numOnStrand)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xff)
    ser.write(serial.to_bytes(bytes))

def sendToServer(serverID):
    port = serverIdPortDict[serverID]
    # import pdb; pdb.set_trace()
    for i in serverLedLists[serverID]:
        strandOnServer = i[0]
        numOnStrand = i[1]
        color = i[2]
        amp = i[3]
        if DRY_RUN:
            pass
            debug("Port: %d, strandOnServer: %d, numOnStrand: %d, color: %d, amp: %d"  %(port, strandOnServer, numOnStrand, color, amp))  
        else:
            setLED(port, strandOnServer, numOnStrand, color, amp)
            

def sendToServers():
    global serverThreads
    
    if serverThreads != []:
        for i in range(NUMBER_OF_SERVERS):
            serverThreads[i].join()

    serverThreads = []
    for i in range(NUMBER_OF_SERVERS):
        serverThreads.append(threading.Thread(target=sendToServer, args=([i]), daemon=True))
        serverThreads[i].start()
