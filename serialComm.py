import Serial

serverIdPortDict = {}
colorAndAmp = []
ports = []
BAUDRATE = 2000000
serverThreads = []

def getID(ser):
    ans = 10
    while ans > 9:
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
            ans = 10
            time.sleep(.5)
    return ans

def begin():
    '''create arduinoID -> port dictionary
    open ports
    '''
    global serverIdPortDict
    
    for i in range(NUMBER_OF_SERVERS):
        ports.append(Serial.serial("/dev/ttyUSB"+i, BAUDRATE))
        serverIdPortDict[getID(ports[i])] = i

def eraseColorAndAmp():
    global colorAndAmp

    colorAndAmp = []
    for i in range(NUMBER_OF_SERVERS):
        colorAndAmp.append([])
        
def addToServer(strand, numOnStrand, colorAndAmp):
    colorAndAmp[strand["arduinoID"]].append([strand, numOnStrand, colorAndAmp[0], colorAndAmp[1]])

def setLED(ser, strand, numOnStrand, color, amplitude):
    bytes = []
    bytes.append((strand << 3) + numOnStrand)
    bytes.append(color)
    bytes.append(amplitude)
    bytes.append(0xff)
    ser.write(serial.to_bytes(bytes))

def sendToServer(serverID):
    port = serverIdPortDict[serverID]
    for i in range(colorAndAmp[serverID]):
        strandOnServer = colorAndAmp[serverID][i][0]["strandOnArduino"]
        numOnStrand = colorAndAmp[serverID][i][1]
        color = colorAndAmp[serverID][i][2]
        amp = colorAndAmp[serverID][i][3]
        setLED(port, strandOnServer, numOnStrand, color, amp)
        
def sendToServers(firstTime):
    global serverThreads
    
    if not(firstTime):
        for i in range(NUMBER_OF_SERVERS):
            serverThreads[i].join

    serverThreads = []
    for i in range(NUMBER_OF_SERVERS):
        serverThreads.append(threading.Thread(targe=sendToServer, args(i), daemon=True)
    
