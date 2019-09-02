import random, time, sys

def getAllStatuses(dict):
    statuses = {}
    for key in dict:
        print(">>>"+key+"<<<")
        status = dict[key]['status']
        if status in statuses.keys():
            statuses[status] = statuses[status] + 1
        else:
            statuses[status] = 1
    print(statuses)

def lefts(key, dict):
    while True:
        key = left(str(key), dict)
        print(key, end=', ')
        sys.stdout.flush()
        time.sleep(1)
    
def left(key, dict):
    return random.choice(dict[key]['left'])
