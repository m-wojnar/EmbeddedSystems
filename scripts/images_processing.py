from time import sleep

import numpy as np
import cv2


LAST_IMG = '/var/lib/motion/lastsnap.jpg'
OUTPUT_IMG = './outputs'

print('START')


while True:
    image = cv2.imread(LAST_IMG)
    
    if image is None:
        sleep(1)
        continue

    original = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3))
    image = cv2.erode(image, kernel, iterations=4)
    image = cv2.dilate(image, kernel, iterations=4)

    contours, _ = cv2.findContours(
        image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    try:
        contours = filter(lambda cont: cv2.arcLength(cont, False) > 1000, contours)
        max_contour = max(contours, key=lambda cont: cv2.contourArea(cont))
    except ValueError:
        sleep(2)
        continue

    rect = cv2.minAreaRect(max_contour)

    if rect[2] > 45:
        rect = (rect[0], (rect[1][1], rect[1][0]), rect[2] - 90)

    box = cv2.boxPoints(rect).astype(np.int0)
    width, height = int(rect[1][0]), int(rect[1][1])

    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    image = cv2.warpPerspective(original, M, (width, height))
    cv2.imwrite(f'{OUTPUT_IMG}/out_{rect[2]}.png', image)

    sleep(1)
