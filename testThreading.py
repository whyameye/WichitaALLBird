import logging
import threading
import time
import serial

def thread_function(name, y):

    logging.info("Thread %s: starting", y)
    for i in range(10):
        ser.write(b'0')
        time.sleep(0.1)
        ser.write(b'1')
        time.sleep(0.1)
    logging.info("Thread %s: finishing", y)

if __name__ == "__main__":
    y = [1]
    ser = serial.Serial('/dev/ttyACM0', 115200)
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    for i in range(2):
        x = threading.Thread(target=thread_function, args=(1,y), daemon=True)
        logging.info("Main    : before running thread")
        x.start()
        time.sleep(5)
        y = [2]
        logging.info("Main    : wait for the thread to finish")
        x.join()
    logging.info("Main    : all done")
