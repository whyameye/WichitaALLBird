import serial, threading, time, os, json
from common import *

serverIdToPortList = []
BAUDRATE = 921600
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

def addToServerLedLists(serverToAssign, ledNum, color, amp):
    if serverToAssign <= (NUMBER_OF_SERVERS - 1):
        serverLedLists[serverToAssign].append([ledNum, color, amp])
    
def resetArduino(port):
    os.system("./dtr "+port)

def getID(ser):
    ans = 10
    while ans > 9:
        log(Log.VERBOSE, "trying to read ID")
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
            ans = 10
            time.sleep(.5)
    return ans

def begin(numOfServers = NUMBER_OF_SERVERS):
    '''create arduinoID -> port dictionary
    open ports
    '''
    global serverIdToPortList
    serverIdToPortList = []
    portToID = []

    for i in range(numOfServers):
        serverIdToPortList.append([])
        log(Log.VERBOSE, "appending to server list")
        
    if DRY_RUN:
        numOfServers = 1

    for i in range(numOfServers):
        resetArduino("/dev/ttyUSB"+str(i))
    time.sleep(2.25) # servers are in program mode for 2 seconds after reset

    try:
        with open('/tmp/portToID.json', 'r') as json_file:
            portToID = json.load(json_file)
            if len(portToID) != numOfServers:
                raise
            log(Log.INFO, "Loading prexisting ID <--> Port map file")
    except:
        for i in range(numOfServers):
            log(Log.INFO, "No ID <--> Port map file found or corrupt. Generating.")
            ser = serial.Serial("/dev/ttyUSB"+str(i), BAUDRATE)
            ser.dtr = False
            ser.rts = False
            time.sleep(.1)
            while ser.in_waiting:  # Or: while ser.inWaiting():
                ser.readline()
            time.sleep(.1)
            serverID = getID(ser)
            log(Log.INFO, "ID: %d Serial /dev/ttyUSB%d" %(serverID, i))
            serverIdToPortList[serverID] = ser
            portToID.append(serverID)
        with open('/tmp/portToID.json', 'w') as outfile:
                json.dump(portToID, outfile)
        return
        
    for i in range(numOfServers):
        ser = serial.Serial("/dev/ttyUSB"+str(i), BAUDRATE)
        ser.dtr = False
        ser.rts = False
        serverID = portToID[i]
        log(Log.INFO, "ID: %d Serial /dev/ttyUSB%d" %(serverID, i))
        serverIdToPortList[serverID] = ser
        
    
def setLED(ser, ledNum, color, amplitude):
    bytes = []
    bytes.append(ledNum >> 8)
    bytes.append(ledNum & 0xFF)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xff)
    log(Log.VERBOSE, "ser: "+ str(ser))
    log(Log.VERBOSE, "ledNum: "+ str(ledNum))
    log(Log.VERBOSE, "color: "+ str(color))
    log(Log.VERBOSE, "amp: "+ str(amplitude))
    ser.write(serial.to_bytes(bytes))

def sendToServer(serverID):
    port = serverIdToPortList[serverID]
    # import pdb; pdb.set_trace()
    if serverLedLists[serverID] == []:
        serverLedLists[serverID].append([31, 0, 0]) # 31 is a nonexistent strand on all servers FIXME
    for i in serverLedLists[serverID]:
        ledNum = i[0]
        color = i[1]
        amp = i[2]
        # time.sleep(.0006) # FIXME
        if DRY_RUN:
            if serverID == DRY_RUN_SERVER:
                # import pdb; pdb.set_trace()
                # print("ServerID: %d, strandOnServer: %d, numOnStrand: %d, color: %d, amp: %d"  %(serverID, strandOnServer, numOnStrand, color, amp))
                setLED(port, ledNum, color, amp)
        else:
            setLED(port, ledNum, color, amp)
            

def sendToServers():
    global serverThreads
    
    if serverThreads != []:
        for i in range(NUMBER_OF_SERVERS):
            serverThreads[i].join()

    serverThreads = []
    for i in range(NUMBER_OF_SERVERS):
        serverThreads.append(threading.Thread(target=sendToServer, args=([i]), daemon=True))
        serverThreads[i].start()
