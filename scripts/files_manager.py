from time import sleep
import os


MOTION_DIR = '/var/lib/motion/'


while True:
    files = sorted(os.listdir(MOTION_DIR))

    for file in files[:-3]:
        os.remove(MOTION_DIR + file)

    sleep(5)

