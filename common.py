import time, sys, select, env


NUMBER_OF_SERVERS = 9

def log(level, msg):
    if level.value >= LOG_LEVEL.value:
        print("%d %s: %s" %(int(round(time.time())), level, msg))

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
