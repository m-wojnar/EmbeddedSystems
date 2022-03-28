import os
import threading

MOTION_DIR = '/var/lib/motion/'


def remove_old_images(interval: float) -> None:
    """
    Removes old images from MOTION_DIR every 'interval' seconds.

    interval: float
        number of seconds between function calls
    """

    files = sorted(os.listdir(MOTION_DIR))

    for file in files[:-3]:
        os.remove(MOTION_DIR + file)

    threading.Timer(interval, remove_old_images, [interval]).start()
