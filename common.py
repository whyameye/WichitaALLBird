from enum import Enum
import time

class Log(Enum):
    VERY_VERBOSE = 1
    VERBOSE = 2
    INFO = 3
    WARNING = 4
    ERROR = 5
LOG_LEVEL = Log.VERBOSE

NUMBER_OF_SERVERS = 10
DRY_RUN = True

def log(level, msg):
    if level.value >= LOG_LEVEL.value:
        print("%d %s: %s" %(int(round(time.time())), level, msg))
