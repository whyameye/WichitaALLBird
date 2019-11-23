#!/usr/bin/python3

import json, time, random, sys
from serialComm import *
from common import *

CHANCE_OF_PICKING_CLOSEST_Y = 0.8

class Seq(object):
    activeLeds = []
    
    def __init__(self, mode):
        self.mode = mode
        self.startTime = millis()
        self.leds = [] # list of LEDs we're currently controlling
        self.totalLeds = random.randrange(self.mode['minLength'],
                                          self.mode['maxLength']+1)
        debug("total LEDs for new sequence: "+str(self.totalLeds))
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
        print("current Strand: "+str(currentStrand))
        print("current LED: "+str(currentLED))
        print("strand to Try: "+str(strandToTry))
        CurrentLEDPos = strands[currentStrand]["y"][currentLED[0][1]]
        PossibleLEDPoses = strands[strandToTry]["y"]
        distances = [abs(i - CurrentLEDPos) for i in PossibleLEDPoses]
        return [strandToTry, distances.index(min(distances)), True]

    def getClosestYIndex(self, currentStrand, currentLEDIndex, nextStrand):
        currentY = strands[currentStrand]["y"][currentLEDIndex]
        deltaY = [abs(currentY - i) for i in strands[nextStrand]["y"]]
        debug("deltaY Index: "+str(deltaY.index(min(deltaY))))
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
        deltaTime = millis() - self.startTime
        if ((deltaTime < (self.currentLedIndex * self.mode['timeToNextLed'])) or
            (self.currentLedIndex >= self.totalLeds)):
            return False
        
        if self.currentLedIndex == 0:
            currentLed = self.getStartLed() # list of 2 elements
            debug("added first led: "+str(currentLed))

        else:
            debug("adding additional LED...")
            currentLed = self.getAdditionalLed()
            if currentLed == False:
                debug("No viable moves. Stunt")
                self.totalLeds = self.currentLedIndex
                return False
            debug("added additional led: "+str(currentLed))
        if currentLed in self.activeLeds:
            if self.currentLedIndex == 0:
                debug("1st LED already in list. Kill the sequence")
                return False
            else:
                debug("found LED already in another active sequence. Stunt")
                self.totalLeds = self.currentLedIndex
                return False
        self.activeLeds.append(currentLed) # all Leds active in all sequences
        debug("activeLEDs: "+str(self.activeLeds));
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
        # debug("RGB: "+str(R)+" "+str(G)+" "+str(B))
        # TODO: set strip color
        # strip.setPixelColor(ledSequence[led[0]],Color(theColors[0],theColors[1],theColors[2]))
        led[0][2] = inPattern
        return inPattern

    def update(self):
        """continually call this high-level update method.
        returns False if all Leds have gone through all states
        """
        self.addLed(self.leds)
        for i in range(len(self.leds)):
            if (not self.updateLed(self.leds[i])):
                debug("removing led: "+str(self.leds[i][0]))
                self.activeLeds.remove(self.leds[i][0])
                debug("active LEDs left:"+str(self.activeLeds));
                debug("sequence LEDs left:"+str(self.leds));

                if (i == (self.totalLeds-1)): # we are rempving the last LED in the sequence
                    # assert(self.leds == [])
                    debug("kill sequence...")
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
        debug("generating parameters for seq #"+str(len(allTheSeqs)+1))
        allTheSeqs.append(Seq(mode))

def updateMode():
    pass

# Main program logic:
if __name__ == '__main__':

    # setup
    allTheSeqs = []
    newTrig = False
    modes = {}
    strands = {}
    strandsInRing = []
    strandsInGroup = []
    mode = 0
    loadGlobalVariables()
    addInniesAndOuties()

    # start in Mode 0
    generateSequences(modes[mode], newTrig)
    begin()
    trigTime = 0

    # loop
    while True:
        # TODO the entire below block is for new modes placeholder for now
        if False: # this is where a new mode would be triggered
            print("NEW MODE")
            newTrig = True # force new sequence to start
            mode = 0 # should be new mode
            trigTime = millis()
        initializeServerLedLists()
        updateMode()
        for sequence in allTheSeqs: # allTheSeqs is a list of classes we will now traverse
            if not sequence.update(): # if sequence should die
                debug("removing sequence")
                sequence.remove() # LWT for the sequence. Probably unnecessary
                allTheSeqs.remove(sequence) # remove from the list
                del sequence # delete class in environment
                # mode = ((millis() - trigTime) < TRIGGER_LENGTH) TODO return to default mode after time period
                generateSequences(modes[mode], newTrig)
        sendToServers()
        time.sleep(.001)
        # strip.show()

