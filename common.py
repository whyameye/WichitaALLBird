from enum import Enum
import time, sys, select, env

NUMBER_OF_SERVERS = 9

class Log(Enum):
    VERY_VERBOSE = 1
    VERBOSE = 2
    INFO = 3
    WARNING = 4
    ERROR = 5

LOG_LEVEL = Log.INFO

def log(level, msg):
    if level.value >= LOG_LEVEL.value:
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        print("%s %s: %s" %(theTime, level, msg), flush=True)

def getInput():
    line = ""
    # If there's input ready, do something, else do something
    # else. Note timeout is zero so select won't block at all.
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
    if line:
        return line
    else:
        return
