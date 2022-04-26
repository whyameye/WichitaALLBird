#!/usr/bin/python3

import json, time, random, sys
from serialComm import *
from common import *

class Seq(object):
    activeLeds = [] # active LEDS for all the sequences not just 1 sequence
    activeSeqs = []
    
    def __init__(self, mode):
        self.mode = mode
        self.leds = [] # list of LEDs we're currently controlling
        self.totalLeds = random.randrange(self.mode['minLength'],
                                          self.mode['maxLength']+1)
        log(Log.VERBOSE, "total LEDs for new sequence: "+str(self.totalLeds))
        self.currentLedIndex = 0 # number of active LEDs in mode
        self.direction = "" #
        self.deleteMe = False
        
    def remove(self):
        pass

    def removeLedUsingActiveLed(self, activeLed, myMillis, firstLed):
        firstEl = [z[0] for z in self.leds]
        myIndex = firstEl.index(activeLed)
        led = self.leds[myIndex]

        if (not firstLed) or (abs(myMillis - self.leds[self.leds.index(led)][1]) > self.mode["overlapTime"]):
            self.removeLed(self.leds.index(led))
            numFalse = [x[0][2] for x in self.leds].count(False)
            if numFalse == len(self.leds):
                self.deleteMe = True
            return True
        else:
            return False
    
    def removeLed(self, led):
        self.activeLeds.remove(self.leds[led][0])
        self.activeSeqs.remove([self, self.leds[led][0]])
        self.leds[led][0][2] = False

    def removeLedIfConflict(self, ledInQuestion, firstLed = False):
        if ledInQuestion in self.activeLeds:
            instanceToCall = self.activeSeqs[self.activeLeds.index(ledInQuestion)][0]
            # if instanceToCall == self:
            #    return True
            if not instanceToCall.removeLedUsingActiveLed(ledInQuestion, millis(), firstLed):
                self.deleteMe = True
                # breakpoint()
                return False
        return True
            
    def getStartLed(self):
        """get first LED in sequence
        returns LED to light described as list: [NUM_OF_SERVER, START_LED #]
        """
        lenStartMoves = len(self.mode["moves"]["startDirection"])
        self.direction = self.mode["moves"]["startDirection"][random.randrange(0,lenStartMoves)]
        startLedList = self.mode['startLeds']
        startLed = startLedList[random.randrange(len(startLedList))]
        if DRY_RUN:
            startServer = DRY_RUN_SERVER
        else:
            startServer = random.randrange(NUMBER_OF_SERVERS)
        startLed = [startServer, startLed, True]
        if self.removeLedIfConflict(startLed, True):
            return startLed
        return False
    
    def getViableMove(self):
        """get a viable move for an already chosen direction.
        returns 1st half of LED list (without millis())
        if no move is viable, return False
        """
        currentLED = self.leds[-1] # get last LED list in list of LED lists
        currentServer = currentLED[0][0]
        currentLedNum = currentLED[0][1]
        if self.direction == "left" and currentServer > 0:
            return [currentServer-1, currentLedNum, True]
        if self.direction == "right" and currentServer < NUMBER_OF_SERVERS-1:
            return [currentServer+1, currentLedNum, True]
        if self.direction == "forward" and currentLedNum < NUMBER_OF_LEDS_PER_SERVER - 1:
            return [currentServer, currentLedNum + 1, True]
        if self.direction == "backward" and currentLedNum > 0:
            return [currentServer, currentLedNum - 1, True]
        return False

    def getAdditionalLed(self):
        """find an Led that meets the criteria
        randomly trying different directions if needed
        returns LED to light described as list: [strand, index of y element in strand]
        returns False if no viable move is possible
        """
        viableMove = self.getViableMove()
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
            if currentLed == False:
                self.deleteMe = True
                return False
            log(Log.VERBOSE, "added first led: "+str(currentLed))
            self.startTime = millis()
            self.activeLeds.append(currentLed) # all Leds active in all sequences
            self.activeSeqs.append([self, currentLed])
            self.leds.append([currentLed, millis()]) # Leds active in this instance only
            self.currentLedIndex = 1
            log(Log.VERY_VERBOSE, "activeLEDs: "+str(self.activeLeds));
            return True
            
        deltaTime = millis() - self.startTime        
        if deltaTime < (self.currentLedIndex * self.mode['timeToNextLed']):
            return True
        if self.currentLedIndex >= self.totalLeds:
            return True
        
        log(Log.VERY_VERBOSE, "adding additional LED...")
        currentLed = self.getAdditionalLed()
        # if currentLed == False:
            # log(Log.VERY_VERBOSE, "No viable moves. Stunt")
            # self.totalLeds = self.currentLedIndex
            # return False
        
        # log(Log.VERY_VERBOSE, "added additional led: "+str(currentLed))
        #if currentLed in self.activeLeds:
            #firstEl = [z[0] for z in self.leds]
            #self.activeLeds.remove(currentLed)
            #self.leds.pop(firstEl.index(currentLed))
        self.removeLedIfConflict(currentLed)
        #if currentLed in self.activeLeds:
        #    if self.currentLedIndex == 0:
        #        log(Log.VERY_VERBOSE, "1st LED already in list. Kill the sequence")
        #        return False
        #    else:
        #        log(Log.VERY_VERBOSE, "found LED already in another active sequence. Stunt")
        #        self.removeLedUsingActiveLed(currentLed)
        #        # self.totalLeds = self.currentLedIndex
        #        return False
        self.activeLeds.append(currentLed) # all Leds active in all sequences
        self.activeSeqs.append([self, currentLed])
        # log(Log.VERY_VERBOSE, "activeLEDs: "+str(self.activeLeds));
        self.leds.append([currentLed, millis()]) # Leds active in this instance only
        self.currentLedIndex += 1

    def updateLed(self,led):
        """Update color of Led based on time
        led passed in is of form [[serverNum, ledNum, T/F active],time]
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
        serverNum = led[0][0]
        ledNum = led[0][1]
        color = colorAndAmp[0]
        amp = colorAndAmp[1]
        addToServerLedLists(serverNum, ledNum, color, amp)
        led[0][2] = inPattern
        return inPattern

    def update(self):
        """continually call this high-level update method.
        returns False if all Leds have gone through all states
        """
        if self.deleteMe:
            self.deleteMe = False
            return False
        if self.addLed(self.leds) == False:
            return False
        for i in range(len(self.leds)):
            if (not self.updateLed(self.leds[i])):
                log(Log.VERBOSE, "removing led: "+str(self.leds[i]))
                # self.activeLeds.remove(self.leds[i][0])
                # self.activeSeqs.remove([self, self.leds[i][0]])
                self.removeLed(i)
                log(Log.VERY_VERBOSE, "active LEDs left:"+str(self.activeLeds));
                log(Log.VERY_VERBOSE, "sequence LEDs left:"+str(self.leds));

                if (i == (self.totalLeds-1)): # we are rempving the last LED in the sequence
                    # assert(self.leds == [])
                    log(Log.VERBOSE, "kill sequence...")
                    return False
        return True

    
def loadJSON(filename):
    f = open(filename,"r")
    jsonResult = json.loads(f.read())
    f.close()
    return jsonResult

def millis():
    return int(round(time.time() * 1000))

def loadGlobalVariables():
    """create list of integers representing strand #s depending on what ring and group they are in
    """
    global modes

    jsonModes = loadJSON("WichitaALLModes.json")

    # indexes that are numeric strings are annoying, so we convert:
    for i in jsonModes:
        modes[int(i)] = jsonModes[i]

def generateSequences(mode, newTrig):
    numOfSeqs = random.randrange(mode['minInstances'],mode['maxInstances']+1)
    while (len(allTheSeqs) < numOfSeqs) or (newTrig == True):
        newTrig = False
        log(Log.VERBOSE, "generating parameters for seq #"+str(len(allTheSeqs)+1))
        allTheSeqs.append(Seq(mode))

def updateMode(modeIndex, trigTime):
    if MODE_FROM_KEYBOARD:
        newIndex = getInput()
        if newIndex:
            trigTime = millis()
            return [int(newIndex[0]), trigTime]
        return [modeIndex, trigTime]
        
# Main program logic:
if __name__ == '__main__':

    # setup
    allTheSeqs = []
    modes = {}
    lastModeIndex = 99 # trigger generation since lastMode != mode
    modeIndex = 0
    loadGlobalVariables()

    begin() # initialize serial communication
    trigTime = millis()
    while True:
        # modeIndex = 0 if ((millis() - trigTime) > TRIGGER_LENGTH) else modeIndex
        modeIndex, trigTime = updateMode(modeIndex, trigTime)
        if lastModeIndex != modeIndex: # new mode triggered
            log(Log.INFO, "NEW MODE: %d" %(modeIndex))
            generateSequences(modes[modeIndex], True)
            lastModeIndex = modeIndex
        initializeServerLedLists()
        log(Log.VERY_VERBOSE, "# of seqs: " + str(len(allTheSeqs)))
        for sequence in allTheSeqs: # allTheSeqs is a list of classes we will now traverse
            if not sequence.update(): # if sequence should die
                log(Log.VERBOSE, "removing sequence")
                sequence.remove() # LWT for the sequence. Probably unnecessary
                allTheSeqs.remove(sequence) # remove from the list
                del sequence # delete class in environment
                generateSequences(modes[modeIndex], False)
        sendToServers()
        # time.sleep(.01)
        # strip.show()

