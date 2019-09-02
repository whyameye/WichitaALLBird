import json, time, random
import serialTest

DEBUG = False

# TODO: this redef of seq ledSequence is odd
ledSequence = seq = [4,5,8,9]

# ledLength = len(loadBirds)

ledLength = len(ledSequence)

modes = {
    0:{
        'minInstances':2,
        'maxInstances':3,
        'minLength':16,
        'maxLength':32,
        'timeToNextLed':100, # ms
        'startLed':range(ledLength),
        'ledPattern':
            [[0,0,0,0], # R,G,B,time
             [0,6,0, 2000],
             [12,12,0, 3000],
             [12,12,0, 4000],
             [12,12,12, 5000],
             [0,0,0,10000]]},
    1:{
        'minInstances':5,
        'maxInstances':5,
        'minLength':32,
        'maxLength':64,
        'timeToNextLed':100, # ms
        'startLed':range(ledLength),
        'ledPattern':
            [[0,0,0,0], # R,G,B,time
             # [255,140,0, 1000],
             [128,0,0, 1400],
             [255,0,0, 1600],
             [178,34,34,2000],
             [255,69,0, 3000],
             [0,0,0,4000]]}}

def saveBirds(birds):
    f = open("birds.json","w")
    f.write(json.dumps(birds, indent=4))
    f.close()
    
def loadBirds(filename):
    f = open(filename,"r")
    birds = json.loads(f.read())
    f.close()
    return birds

def debug(str):
    if DEBUG:
        print("DEBUG: "+str)

def millis():
    return int(round(time.time() * 1000))

class Seq(object):
    activeLeds = []
    
    def __init__(self, mode):
        self.mode = mode
        self.startTime = millis()
        self.leds = []
        self.totalLeds = random.randrange(self.mode['minLength'],
                                          self.mode['maxLength']+1)
        debug("total LEDs for new sequence: "+str(self.totalLeds))
        self.currentLed = 0
        
    def remove(self):
        pass

    def addLed(self,leds):
        deltaTime = millis() - self.startTime
        if ((deltaTime >= (self.currentLed * self.mode['timeToNextLed'])) and
            (self.currentLed < self.totalLeds)):
            debug("adding LED:")
            if self.currentLed == 0:
                ledIndex = random.randrange(len(self.mode['startLed']))
                debug("adding first led: "+str(ledIndex))
            else:
                # FIXME: how to choose ledIndex
                ledIndex = (self.leds[self.currentLed-1][0]+1) % len(ledSequence)
                debug("adding additional led: "+str(ledIndex))
            if ledIndex in self.activeLeds:
                if self.currentLed == 0:
                    debug("1st LED already in list. Kill the sequence")
                    return False
                else:
                    debug("found LED already in another active sequence. Stunt")
                    self.totalLeds = self.currentLed
                    return True
            self.activeLeds.append(ledIndex)
            debug("activeLEDs: "+str(self.activeLeds));
            self.leds.append([ledIndex, millis()])
            self.currentLed += 1
        return True

    def updateLed(self,led):
        deltaTime = millis() - led[1]
        ledPatterns = (self.mode['ledPattern'])
        inPattern = False
        for j in range(len(ledPatterns)):
            theColors = [0,0,0]
            if ledPatterns[j][3] > deltaTime:
                ddTime = 0.0 + deltaTime - ledPatterns[j-1][3]
                tTime = 0.0 + ledPatterns[j][3] - ledPatterns[j-1][3]
                for k in range(3):
                    diffColor = ledPatterns[j][k] - ledPatterns[j-1][k]
                    theColors[k]=int(round(ddTime*(diffColor/tTime)+ledPatterns[j-1][k]))
                inPattern = True
                break;
            
        # debug("RGB: "+str(R)+" "+str(G)+" "+str(B))
        # TODO: set strip color
        # strip.setPixelColor(ledSequence[led[0]],Color(theColors[0],theColors[1],theColors[2]))
        return inPattern

    # continually call this high-level update method
    # returns False if all Leds have gone through all states
    def update(self):
        if not self.addLed(self.leds):
            return False
        for i in range(len(self.leds)):
            if (not self.updateLed(self.leds[i])):
                # debug("updateLed: "+str(self.leds[i]))
                try:
                    self.activeLeds.remove(self.leds[i][0])
                except:
                    # self.leds.remove(self.leds[i])
                    if (i == (self.totalLeds-1)):
                        # assert(self.leds == [])
                        debug("kill sequence...")
                        return False
        return True


def generateSequences(mode, newTrig):
    numOfSeqs = random.randrange(mode['minInstances'],mode['maxInstances']+1)
    while (len(allTheSeqs) < numOfSeqs) or (newTrig == True):
        newTrig = False
        debug("generating seq #"+str(len(allTheSeqs)+1))
        allTheSeqs.append(Seq(mode))

def updateMode():
    pass

# Main program logic:
if __name__ == '__main__':

    # setup
    mode = 0
    allTheSeqs = []
    newTrig = False
    generateSequences(modes[mode], newTrig)
    trigTime = 0
    
    # loop
    while True:
        # TODO the entire below block is for new modes placeholder for now
        if False: # this is where a new mode would be triggered
            print("NEW MODE")
            newTrig = True
            mode = 0 # should be new mode
            trigTime = millis()
        updateMode()
        for sequence in allTheSeqs:
            if not sequence.update():
                debug("removing sequence")
                sequence.remove()
                allTheSeqs.remove(sequence)
                del sequence
                mode = ((millis() - trigTime) < TRIGGER_LENGTH)
                generateSequences(modes[mode], newTrig)
        # strip.show()

            
            
