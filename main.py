#!/usr/bin/python3

import json, time, random, sys
from serialComm import *
from common import *
import redis

CHANCE_OF_PICKING_CLOSEST_Y = 0.8
class Seq(object):
    activeLeds = []
    
    def __init__(self, mode):
        self.mode = mode
        self.leds = [] # list of LEDs we're currently controlling
        self.totalLeds = random.randrange(self.mode['minLength'],
                                          self.mode['maxLength']+1)
        log(Log.VERBOSE, "total LEDs for new sequence: "+str(self.totalLeds))
        self.currentLedIndex = 0 # number of active LEDs in mode
        self.direction = "" #
        
    def remove(self):
        pass

    def getStartLed(self):
        """get first LED in sequence
        returns LED to light described as list: [strand, index of y element in strand]
        """

        possibleStartRings = self.mode["moves"]["startRings"]
        possibleStartGroups = self.mode["moves"]["startGroups"]
        possibleStrandsInRings = []
        for i in possibleStartRings:
            possibleStrandsInRings += strandsInRing[i]
        possibleStrandsInGroups = []
        for i in possibleStartGroups:
            possibleStrandsInGroups += strandsInGroup[i]
        possibleStrands = list(set(possibleStrandsInRings) & set(possibleStrandsInGroups))
        theChosenStrandIndex = random.randrange(0,len(possibleStrands))
        theChosenStrand = possibleStrands[theChosenStrandIndex]
        lenStartMoves = len(self.mode["moves"]["startDirection"])
        self.direction = self.mode["moves"]["startDirection"][random.randrange(0,lenStartMoves)]
        LedIndexOnStrand = random.randrange(0,len(strands[theChosenStrand]["y"]))
        return [theChosenStrand, LedIndexOnStrand, True]

    def chooseLEDOnStrand(self, currentLED, currentStrand, strandToTry):
        if (random.random() > CHANCE_OF_PICKING_CLOSEST_Y):
            return [strandToTry, random.randrange(0,len(strands[strandToTry]["y"])), True]
        log(Log.VERY_VERBOSE, "current Strand: "+str(currentStrand))
        log(Log.VERY_VERBOSE, "current LED: "+str(currentLED))
        log(Log.VERY_VERBOSE, "strand to Try: "+str(strandToTry))
        CurrentLEDPos = strands[currentStrand]["y"][currentLED[0][1]]
        PossibleLEDPoses = strands[strandToTry]["y"]
        distances = [abs(i - CurrentLEDPos) for i in PossibleLEDPoses]
        return [strandToTry, distances.index(min(distances)), True]

    def getClosestYIndex(self, currentStrand, currentLEDIndex, nextStrand):
        currentY = strands[currentStrand]["y"][currentLEDIndex]
        deltaY = [abs(currentY - i) for i in strands[nextStrand]["y"]]
        log(Log.VERY_VERBOSE, "deltaY Index: "+str(deltaY.index(min(deltaY))))
        return deltaY.index(min(deltaY))
    
    def getViableMove(self):
        """get a viable move for an already chosen direction.
        returns 1st half of LED list (without millis())
        if no move is viable, return False
        """
        currentLED = self.leds[-1] # get last LED list in list of LED lists 
        currentStrand = currentLED[0][0]
        currentLEDIndexOnStrand = currentLED[0][1]
        if self.direction == "left" or self.direction == "right":
            try:
                possibleStrands = strands[currentStrand][self.direction].copy()
            except KeyError:
                return False
            while len(possibleStrands) > 0:
                i = random.randrange(0,len(possibleStrands))
                strandToTry = possibleStrands.pop(i)
                if self.testViableMove(currentStrand, strandToTry):
                    return self.chooseLEDOnStrand(currentLED, currentStrand, strandToTry)
            return False
        if self.direction == "up" and currentLEDIndexOnStrand > 0:
            return [currentStrand, currentLEDIndexOnStrand - 1, True]
        if self.direction == "down" and currentLEDIndexOnStrand < (len(strands[currentStrand]["y"])-1):
            return [currentStrand, currentLEDIndexOnStrand + 1, True]
        for i in ["inner", "outer"]:
            if self.direction == i and strands[currentStrand].get(i):
                nextStrand = strands[currentStrand][i]
                return [nextStrand,
                        self.getClosestYIndex(currentStrand, currentLEDIndexOnStrand, nextStrand), True]
        return False

    def testViableMove(self,currentStrand, strandToTry):
        if (self.mode["moves"]["moveOutsideGroup"].upper() == "N" and
            strands[currentStrand]["group"] != strands[strandToTry]["group"]):
            return False
        if (self.mode["moves"]["moveOutsideRing"].upper() == "N" and
            strands[currentStrand]["ring"] != strands[strandToTry]["ring"]):
            return False
        return True
        

    def getAdditionalLed(self):
        """find an Led that meets the criteria
        randomly trying different directions if needed
        returns LED to light described as list: [strand, index of y element in strand]
        returns False if no viable move is possible
        """
        viableMove = self.getViableMove() if random.random() > self.mode["moves"]["changeMove"] else False
        if viableMove == False:
            movesAllowed = self.mode["moves"]["movesAllowed"].copy()
            numMovesAllowed = len(movesAllowed)

        while viableMove == False:
            if numMovesAllowed == 0:
                return False
            self.direction = movesAllowed.pop(random.randrange(0,numMovesAllowed))
            viableMove = self.getViableMove()
            numMovesAllowed -= 1
        return viableMove

    def addLed(self,leds):
        """add first or next LED in sequence
        returns True if LED was successfully added, otherwise False
        """

        if self.currentLedIndex == 0:
            currentLed = self.getStartLed() # list of 2 elements
            log(Log.VERBOSE, "added first led: "+str(currentLed))
            self.startTime = millis()
            self.currentLedIndex = 1
            self.activeLeds.append(currentLed) # all Leds active in all sequences
            log(Log.VERY_VERBOSE, "activeLEDs: "+str(self.activeLeds));
            self.leds.append([currentLed, millis()]) # Leds active in this instance only
            return True
            
        deltaTime = millis() - self.startTime        
        if ((deltaTime < (self.currentLedIndex * self.mode['timeToNextLed'])) or
            (self.currentLedIndex >= self.totalLeds)):
            return False
        
        log(Log.VERY_VERBOSE, "adding additional LED...")
        currentLed = self.getAdditionalLed()
        if currentLed == False:
            log(Log.VERY_VERBOSE, "No viable moves. Stunt")
            self.totalLeds = self.currentLedIndex
            return False
        
        # log(Log.VERY_VERBOSE, "added additional led: "+str(currentLed))
        if currentLed in self.activeLeds:
            if self.currentLedIndex == 0:
                log(Log.VERY_VERBOSE, "1st LED already in list. Kill the sequence")
                return False
            else:
                log(Log.VERY_VERBOSE, "found LED already in another active sequence. Stunt")
                self.totalLeds = self.currentLedIndex
                return False
        self.activeLeds.append(currentLed) # all Leds active in all sequences
        # log(Log.VERY_VERBOSE, "activeLEDs: "+str(self.activeLeds));
        self.leds.append([currentLed, millis()]) # Leds active in this instance only
        self.currentLedIndex += 1

    def updateLed(self,led):
        """Update color of Led based on time
        led passed in is of form [[strand, # on strand, T/F active],time]
        returns False only if led state is changing from active to inactive
        """
        if led[0][2] == False: # inactive LED
            return True
        
        deltaTime = millis() - led[1]
        ledPatterns = self.mode['ledPattern']
        inPattern = False
        for j in range(len(ledPatterns)):
            colorAndAmp = [0,0]
            if ledPatterns[j][2] > deltaTime:
                ddTime = 0.0 + deltaTime - ledPatterns[j-1][2]
                tTime = 0.0 + ledPatterns[j][2] - ledPatterns[j-1][2]
                for k in range(2):
                    diffColorOrAmp = ledPatterns[j][k] - ledPatterns[j-1][k]
                    colorAndAmp[k]=int(round(ddTime*(diffColorOrAmp/tTime)+ledPatterns[j-1][k]))
                inPattern = True
                break;
        strand = strands[led[0][0]]
        serverToAssign = strand["arduinoID"]
        strandOnServer = strand["strandOnArduino"]
        numOnStrand = led[0][1]
        color = colorAndAmp[0]
        amp = colorAndAmp[1]
        addToServerLedLists(serverToAssign, strandOnServer, numOnStrand, color, amp)
        led[0][2] = inPattern
        return inPattern

    def update(self):
        """continually call this high-level update method.
        returns False if all Leds have gone through all states
        """
        self.addLed(self.leds)
        for i in range(len(self.leds)):
            if (not self.updateLed(self.leds[i])):
                log(Log.VERBOSE, "removing led: "+str(self.leds[i]))
                self.activeLeds.remove(self.leds[i][0])
                log(Log.VERY_VERBOSE, "active LEDs left:"+str(self.activeLeds));
                log(Log.VERY_VERBOSE, "sequence LEDs left:"+str(self.leds));

                if (i == (self.totalLeds-1)): # we are rempving the last LED in the sequence
                    # assert(self.leds == [])
                    log(Log.VERBOSE, "kill sequence...")
                    return False
        return True


def saveBirds(birds):
    f = open("birds.json","w")
    f.write(json.dumps(birds, indent=4))
    f.close()
    
def loadJSON(filename):
    f = open(filename,"r")
    jsonResult = json.loads(f.read())
    f.close()
    return jsonResult

def millis():
    return int(round(time.time() * 1000))

def addInniesAndOuties():
    """adds closest inner and outer to json"""
    for outerRing in range(1,3):
        for strandInOuterRing in strandsInRing[outerRing]:
            # print("outer: "+str(strandInOuterRing))
            distances = []
            for strandInInnerRing in strandsInRing[outerRing+1]:
                # print("inner: "+str(strandInInnerRing))
                if strandInInnerRing != strandInOuterRing:
                    deltaX = (strands[strandInOuterRing]["x"] -
                              strands[strandInInnerRing]["x"])
                    deltaZ = (strands[strandInOuterRing]["z"] -
                              strands[strandInInnerRing]["z"])
                    distances.append(deltaX**2 + deltaZ**2)
                else:
                    distances.append(sys.maxsize) # add it for indexing but make it unpickable
                    # print("EQUAL")


            closestInner = strandsInRing[outerRing+1][distances.index(min(distances))]
            # print("outer: "+str(strandInOuterRing))
            # print("inner: "+str(closestInner))
            strands[strandInOuterRing]["inner"]=closestInner
            strands[closestInner]["outer"]=strandInOuterRing


def loadGlobalVariables():
    """create list of integers representing strand #s depending on what ring and group they are in
    """
    global strandsInRing, strandsInGroup, modes, strands

    jsonModes = loadJSON("WichitaALLModes.json")
    jsonStrands = loadJSON("WichitaALLStrands.json")

    # indexes that are numeric strings are annoying, so we convert:
    for i in jsonModes:
        modes[int(i)] = jsonModes[i]
    for i in jsonStrands:
        strands[int(i)] = jsonStrands[i]

    # make a list of which strands are in which rings and groups:
    for i in range(4):
        strandsInRing.append([])
        strandsInGroup.append([])
    for i in strands:
        for j in range(1,4):
            if j in strands[i]["ring"]:
                strandsInRing[j].append(i)
            if j in strands[i]["group"]:
                strandsInGroup[j].append(i)


def generateSequences(mode, newTrig):
    numOfSeqs = random.randrange(mode['minInstances'],mode['maxInstances']+1)
    while (len(allTheSeqs) < numOfSeqs) or (newTrig == True):
        newTrig = False
        log(Log.VERBOSE, "generating parameters for seq #"+str(len(allTheSeqs)+1))
        allTheSeqs.append(Seq(mode))

def updateMode(modeIndex, trigTime):
    if env.MODE_FROM_KEYBOARD:
        newIndex = getInput()
        if newIndex:
            trigTime = millis()
            modeIndex = int(newIndex[0])

    if env.TEST_SENSORS or not env.MODE_FROM_KEYBOARD:
        for i in range(1,8):
            strFromSensor = r.get("from/"+str(i))
            if strFromSensor != None:
                try:
                    activity = json.loads(strFromSensor)["activity"]
                    if activity == True:
                        log(Log.INFO,"Sensor "+str(i)+" activated")
                        if not env.MODE_FROM_KEYBOARD:
                            trigTime = millis()
                            modeIndex = i
                except:
                    pass
    return [modeIndex, trigTime]
    
# Main program logic:
if __name__ == '__main__':

    # setup
    allTheSeqs = []
    modes = {}
    strands = {}
    strandsInRing = []
    strandsInGroup = []
    lastModeIndex = 99 # trigger generation since lastMode != mode
    modeIndex = 0
    loadGlobalVariables()
    addInniesAndOuties()

    begin() # initialize serial communication
    trigTime = millis()
    r = redis.StrictRedis(host='localhost', port=6379, db=1,
                          password=env.redisPassword,
                          charset="utf-8",decode_responses=True)
    # loop
    while True:
        modeIndex = 0 if ((millis() - trigTime) > env.TRIGGER_LENGTH) else modeIndex
        modeIndex, trigTime = updateMode(modeIndex, trigTime)
        if lastModeIndex != modeIndex: # new mode triggered
            log(Log.INFO, "NEW MODE: %d" %(modeIndex))
            generateSequences(modes[modeIndex], True)
            lastModeIndex = modeIndex
        initializeServerLedLists()
        for sequence in allTheSeqs: # allTheSeqs is a list of classes we will now traverse
            if not sequence.update(): # if sequence should die
                log(Log.VERBOSE, "removing sequence")
                sequence.remove() # LWT for the sequence. Probably unnecessary
                allTheSeqs.remove(sequence) # remove from the list
                del sequence # delete class in environment
                generateSequences(modes[modeIndex], False)
        sendToServers()
        time.sleep(.01)
        # strip.show()

