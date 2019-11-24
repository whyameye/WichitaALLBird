from enum import Enum

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
        print("%s: %s" %(level, msg))
