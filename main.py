import json, time, random
import serialTest

DEBUG = True
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
        possibleStrands = list(set(possibleStartRings) & set(possibleStartGroups))
        theChosenStrandIndex = random.randrange(0,len(possibleStrands))
        theChosenStrand = possibleStrands[theChosenStrandIndex]
        lenStartMoves = len(self.mode["moves"]["startDirection"])
        self.direction = self.mode["moves"]["startDirection"][random.randrange(0,lenStartMoves)]
        LedIndexOnStrand = random.randrange(0,len(strands[theChosenStrand]["y"])+1)
        return [theChosenStrand, LedIndexOnStrand, True]

    def getViableMove(self):
        currentLED = self.activeLEDs[-1] # get last LED list in list of LED lists 
        currentStrand = currentLED[0]
        currentLEDIndexOnStrand = currentLED[1]
        if self.direction == "left" or self.direction == "right":
            try:
                possibleStrands = strands[currentStrand][self.direction].copy()
            except KeyError:
                return False
            while len(possibleStrands) > 0:
                i = random.randrange(0,len(possibleStrands))
                strandToTry = possibleStrands.pop(i)
                if testViableMove(currentStrand, strandToTry):
                    return chooseLEDOnStrand(currentStrand, strandToTry)
            return False
        if self.direction == "up" and currentLEDOnStrand > 0:
            return [currentStrand, currentLEDOnStrand - 1]
        if self.direction == "down" and currentLEDOnStrand < len(strands[currentStrand]["y"]):
            return [currentStrand, currentLEDOnStrand + 1]
        return False

    def testViableMove(self,currentStrand, strandToTry):
        if (modes[mode]["moveOutsideGroup"] == "N" and
            strands[currentStrand]["group"] != strands[strandToTry]["group"]):
            return False
        if (modes[mode]["moveOutsideRing"] == "N" and
            strands[currentStrand]["ring"] != strands[strandToTry]["ring"]):
            return False
        

    def getAdditionalLed(self):
        """find an Led that meets the criteria
        randomly trying different directions if needed
        """
        viableMove = getViableMove() if random.random > modes[self.mode]["changeMove"] else False
        if viableMove == False:
            movesAllowed = modes[self.mode]["movesAllowed"].copy()
            numMovesAllowed = len(movesAllowed)

        while viableMove == False:
            if numMovesAllowed == 0:
                return False
            self.direction = movesAllowed.pop(random.randrange(0,numMovesAllowed))
            viableMove = getViableMove()
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
            currentLed = self.getAdditionalLed()
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


    def chooseLEDOnStrand(currentStrand, strandToTry):
        if (random.random > CHANCE_OF_PICKING_CLOSEST_Y):
            return [strandToTry, random.randrange(0,len(strands[testStrand]["y"])+1)]
        CurrentLEDPos = strands[currentLED[0]]["y"][currentLED[1]]
        PossibleLEDPoses - strands[strandToTry]["y"]
        distances = [abs(i - CurrentLEDPos) for i in PossibleLEDPoses]
        return distances.index(min(distances))
                         
        

    def updateLed(self,led):
        """Update color of Led based on time
        led passed in is off form [[strand, # on strand],time]
        returns False unly if led state is changing from active to inactive
        """
        if led[0][2] == False: # inactive LED
            return True
        
        deltaTime = millis() - led[1]
        ledPatterns = self.mode['ledPattern']
        inPattern = False
        for j in range(len(ledPatterns)):
            theColors = [0,0,0]
            if ledPatterns[j][2] > deltaTime:
                ddTime = 0.0 + deltaTime - ledPatterns[j-1][2]
                tTime = 0.0 + ledPatterns[j][2] - ledPatterns[j-1][2]
                for k in range(2):
                    diffColor = ledPatterns[j][k] - ledPatterns[j-1][k]
                    theColors[k]=int(round(ddTime*(diffColor/tTime)+ledPatterns[j-1][k]))
                inPattern = True
                break;
            
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
                self.activeLeds.remove(self.leds[i][0])
                if (i == (self.totalLeds-1)):
                    assert(self.leds == [])
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

def debug(str):
    if DEBUG:
        print("DEBUG: "+str)

def millis():
    return int(round(time.time() * 1000))

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
    loadGlobalVariables()

    # start in Mode 0
    generateSequences(modes[0], newTrig)
    trigTime = 0
    
    # loop
    while True:
        break;
        # TODO the entire below block is for new modes placeholder for now
        if False: # this is where a new mode would be triggered
            print("NEW MODE")
            newTrig = True # force new sequence to start
            mode = 0 # should be new mode
            trigTime = millis()
        updateMode()
        for sequence in allTheSeqs: # allTheSeqs is a list of classes we will now traverse
            if not sequence.update(): # if sequence should die
                debug("removing sequence")
                sequence.remove() # LWT for the sequence. Probably unnecessary
                allTheSeqs.remove(sequence) # remove from the list
                del sequence # delete class in environment
                # mode = ((millis() - trigTime) < TRIGGER_LENGTH) TODO
                generateSequences(modes[mode], newTrig)
        # strip.show()
