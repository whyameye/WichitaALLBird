import time, random
import alsaaudio, time, audioop

from neopixel import *

ledSequence = seq = [458, 459, 386, 387, 388, 389, 456, 457, 492, 491, 490, 489, 461, 460, 383, 384, 385, 361, 360, 359, 358, 357, 356, 390, 391, 453, 454, 455, 494, 493, 552, 553, 554, 555, 485, 486, 488, 484, 487, 463, 462, 381, 382, 364, 363, 362, 273, 272, 274, 275, 276, 277, 279, 278, 284, 355, 354, 393, 392, 451, 452, 498, 499, 546, 547, 548, 549, 495, 496, 497, 547, 548, 549, 550, 551, 573, 572, 572, 571, 570, 556, 557, 558, 559, 560, 482, 483, 465, 464, 466, 380, 379, 366, 365, 269, 270, 271, 272, 274, 275, 251, 250, 249, 248, 280, 281, 282, 283, 285, 353, 352, 394, 395, 450, 449, 500, 501, 544, 545, 579, 578, 577, 576, 574, 619, 620, 621, 622, 569, 568, 567, 566, 565, 564, 563, 562, 561, 481, 480, 479, 468, 467, 378, 369, 377, 370, 372, 373, 374, 473, 472, 474, 475, 476, 477, 478, 479, 468, 469, 376, 375, 471, 472, 474, 475, 476, 477, 478, 470, 471, 367, 368, 265, 264, 263, 261, 262, 161, 162, 259, 258, 257, 256, 268, 267, 266, 260, 259, 162, 160, 159, 158, 157, 156, 67, 68, 152, 151, 149, 148, 171, 172, 252, 170, 253, 254, 255, 166, 165, 164, 155, 154, 153, 169, 168, 167, 166, 66, 69, 628, 627, 626, 634, 633, 632, 628, 629, 613, 614, 615, 616, 617, 625, 618, 624, 636, 635, 634, 633, 632, 631, 630, 611, 610, 583, 582, 542, 543, 544, 545, 579, 580, 581, 582, 542, 543, 503, 502, 447, 448, 396, 397, 351, 350, 289, 290, 291, 292, 240, 241, 242, 287, 286, 282, 281, 280, 248, 249,173, 172, 171, 169, 153, 152, 68, 66, 69, 70, 71, 150, 146, 145, 147, 174, 173, 174, 175, 176, 144, 143, 74, 73, 72, 60, 61, 64, 65, 63, 62, 56, 57, 55, 54, 1, 2, 3, 4, 5, 46, 47, 48, 53, 52, 58, 59, 75, 76, 77, 142, 141, 177, 178, 179, 245, 246, 247, 175, 176, 177, 178, 179, 245, 244, 243, 238, 239, 237, 236, 185, 186, 187, 188, 189, 131, 130, 90, 91, 35, 34, 11, 10, 9, 8, 7, 6, 5, 46, 45, 44, 49, 50, 51, 52, 53, 48, 49, 50, 78, 79, 140, 139, 138, 180, 181, 182, 183, 184, 134, 133, 132, 88, 89, 36, 37, 38, 39, 40, 41, 42, 43, 80, 81, 137, 136, 83, 135, 87, 86, 85, 84, 82, 513, 514, 515, 516, 530, 531, 532, 512, 513, 514, 515, 432, 431, 430, 429, 520, 519, 518, 517, 516, 530, 531, 532, 533, 534, 535, 536, 537, 509, 510, 511, 512, 513, 514, 434, 433, 415, 416, 417, 428, 427, 426, 521, 522, 523, 524, 526, 525, 597, 596, 598, 595, 529, 528, 527, 526, 525, 597, 596, 598, 595,594, 599, 600, 601, 602, 603, 604, 605, 606, 586, 585, 540, 541, 504, 505, 445, 444, 443, 442, 403, 404, 405, 409, 410, 411, 336, 335, 334, 303, 304, 225, 224, 194, 193, 227,226, 301, 300, 299, 298, 342, 343, 345, 344, 341, 340, 339, 338, 337, 302, 303, 218, 217, 216, 215, 214, 313, 312, 311, 310, 309, 308, 220, 219, 201, 202, 203, 204, 205, 212, 213, 318, 317, 316, 315, 314, 327, 328, 329, 330, 306, 305, 307, 223, 222, 221, 198, 199, 200, 117, 116, 115, 114, 113, 206, 208, 207, 112, 111, 110, 109, 108, 107, 106, 118, 119, 120, 121, 197, 122, 196, 124, 125, 192, 191, 190, 231, 232, 233, 234, 235, 293, 294, 346, 347, 349, 348, 398, 400, 401, 402, 344, 345, 346, 347, 349, 348, 398, 399, 446, 445, 505, 504, 541, 540, 585, 584, 608, 609, 610, 611, 612, 613, 614, 615, 577, 576, 575, 574, 619, 620, 28, 98, 99, 26, 27, 29, 30, 95, 96, 97, 127, 126, 123, 100, 101, 102, 25, 24, 16, 15, 14, 13, 12, 29, 30, 31, 32, 92, 94, 93, 129, 128, 191, 192, 228, 230, 229, 297, 296, 295, 294, 346, 347, 349, 348, 401, 402, 344, 345, 346, 347, 349, 348, 398, 399, 446, 445, 505, 504, 541, 540, 585, 584, 608, 609, 610, 611, 612, 613, 614, 615, 577, 576, 575, 574, 619, 620, 623, 593, 592, 591, 590, 589, 588, 587, 539, 538, 506, 507, 508, 440, 441, 406, 407, 408, 436, 437, 438, 439, 440, 441, 406, 407, 408, 436, 435, 412, 413, 414, 332, 331, 418, 419, 420, 421, 424, 422, 423, 323, 324, 325, 326, 420, 421, 424, 422, 423, 323, 322, 321, 320, 319, 210, 211, 209, 208, 206, 113, 114, 115, 116, 117, 118, 119, 103, 104, 23, 22, 21, 20, 19, 18, 17, 108, 107, 106, 105, 20, 561, 562, 477, 478, 470, 469, 468, 467, 378, 369, 368, 265, 264, 371, 370, 377, 378, 379, 366, 365, 269, 268, 256, 257, 258, 259, 162, 161, 33, 34, 35, 89, 88, 132, 131, 189, 190, 191, 192, 1125, 124, 196, 195, 222, 223, 326, 325, 324, 323, 423, 422, 424, 425, 426, 521, 520, 429, 428, 427, 583, 582, 581, 612, 611, 610, 609, 608, 607, 606, 586, 587, 53, 535, 534, 533, 532, 531, 530, 529, 528, 596, 597, 288, 287, 286, 282, 283, 285, 353, 288, 289, 290, 291, 292, 240, 239, 238, 243, 244, 245, 246, 247, 175, 174, 147, 148, 149, 151, 152, 68, 67, 156, 157, 158, 159, 163, 304, 305, 306, 333, 334, 303, 304, 225, 224, 223, 307, 308, 309, 310, 329, 330, 331, 332, 333]

TRIGGER_VOLUME = 500 # AUDIO TRIGGER VOLUME. LOWER = MORE SENSITIVE
TRIGGER_LENGTH = 10000 # ms for the trigger to last

LED_COUNT      = 636 # len(ledSequence)      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!)            
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)       
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)     
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest           
LED_INVERT     = False   # True to invert the signal (when using NPN transistor)

DEBUG = False
modes = {
    0:{
        'nextMode':{0:100}, # 100% chance that next mode will be 0
        'minInstances':2,
        'maxInstances':3,
        'minLength':16,
        'maxLength':32,
        'timeToNextLed':100, # ms
        'startLed':range(len(ledSequence)),
        'ledPattern':
            [[0,0,0,0], # R,G,B,time
             [0,6,0, 2000],
             [12,12,0, 3000],
             [12,12,0, 4000],
             [12,12,12, 5000],
             [0,0,0,10000]]},
    1:{
        'nextMode':{0:100}, # 100% chance that next mode will be 0
        'minInstances':5,
        'maxInstances':5,
        'minLength':32,
        'maxLength':64,
        'timeToNextLed':100, # ms
        'startLed':range(len(ledSequence)),
        'ledPattern':
            [[0,0,0,0], # R,G,B,time
             # [255,140,0, 1000],
             [128,0,0, 1400],
             [255,0,0, 1600],
             [178,34,34,2000],
             [255,69,0, 3000],
             [0,0,0,4000]]}}

# ONLY THE CODE LIVES BELOW THIS LINE, NO PARAMETERS (I HOPE)

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK,'system')
inp.setchannels(1)
inp.setrate(8000)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
# The period size controls the internal number of frames per period.
inp.setperiodsize(160)

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
        strip.setPixelColor(ledSequence[led[0]],Color(theColors[0],theColors[1],theColors[2]))
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
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    mode = 0
    allTheSeqs = []
    newTrig = False
    generateSequences(modes[mode], newTrig)
    trigTime = 0

    # loop
    while True:
        l,data = inp.read()
        if l:
            # Return the maximum of the absolute value of all samples in a fragment.
            try:
                if audioop.max(data, 2) > TRIGGER_VOLUME:
                    print("TRIGGER ACTIVATED")
                    newTrig = True
                    trigTime = millis()
            except:
                pass
        updateMode()
        for sequence in allTheSeqs:
            if not sequence.update():
                debug("removing sequence")
                sequence.remove()
                allTheSeqs.remove(sequence)
                del sequence
                mode = ((millis() - trigTime) < TRIGGER_LENGTH)
                generateSequences(modes[mode], newTrig)
        strip.show()
        # time.sleep(.01)
