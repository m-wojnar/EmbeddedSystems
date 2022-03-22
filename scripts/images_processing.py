from time import sleep

import numpy as np
import cv2


LAST_IMG = '/var/lib/motion/lastsnap.jpg'


while True:
    img = cv2.imread(LAST_IMG, cv2.IMREAD_GRAYSCALE)
    img_eq = cv2.equalizeHist(img)

    cv2.imwrite('equalized.png', img_eq)
    sleep(1)

