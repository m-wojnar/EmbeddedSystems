import json

import cv2
import numpy as np

MIN_AREA, MAX_AREA = 0.003, 0.100
MIN_RATIO, MAX_RATIO = 4, 5

RECTS_IMG = './server/static/rects.png'
PROCESSED_IMG = './server/static/processed.png'
INDEXED_IMG = './server/static/indexed.png'

with open('./config.json', 'r') as file:
    config = json.load(file)


def find_plates(image: np.ndarray) -> list[np.ndarray]:
    """
    Extracts licence plates images from given image

    image: np.ndarray
        image to process

    returns: list[np.ndarray]
        list of images with extraced plates
    """

    full_area = image.shape[0] * image.shape[1]
    min_area, max_area = full_area * MIN_AREA, full_area * MAX_AREA

    processed = _preprocess_image(image)
    segment_count, indexed, stats, _ = cv2.connectedComponentsWithStats(
        processed, 8, cv2.CV_32S)

    idx_copy = indexed.copy().astype(np.float64)
    idx_copy *= 255 / segment_count
    idx_copy = cv2.applyColorMap(idx_copy.astype(np.uint8), cv2.COLORMAP_HSV)

    if config['save_images']:
        cv2.imwrite(PROCESSED_IMG, processed)
        cv2.imwrite(INDEXED_IMG, idx_copy)

    plates = []
    image_rects = image.copy()

    for i in range(1, segment_count):
        area = stats[i, cv2.CC_STAT_AREA]

        if min_area < area < max_area:
            segment = (indexed == i).astype('uint8') * 255
            plate = _crop_plate(segment, image, image_rects)
            ratio = plate.shape[1] / plate.shape[0]

            if MIN_RATIO < ratio < MAX_RATIO:
                plate = _preproces_plate(plate)
                plates.append(plate)

    if config['save_images']:
        cv2.imwrite(RECTS_IMG, image_rects)

    return plates


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Prepares image for licence plates extraction 

    image: np.ndarray
        original image

    returns: np.ndarray
        processed image
    """

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((3, 3))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    _, image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return image


def _crop_plate(segment: np.ndarray, image: np.ndarray, image_rects: np.ndarray) -> np.ndarray:
    """
    Extracts licence plates images from given image

    segment: np.ndarray
        selected segment

    image: np.ndarray
        original image

    image_rects: np.ndarray
        copy of the original image to draw boxes of found plates

    returns: np.ndarray
        cropped license plate
    """

    contours, _ = cv2.findContours(
        segment, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=lambda cont: cv2.contourArea(cont))

    rect = cv2.minAreaRect(max_contour)

    if rect[2] > 45:
        rect = (rect[0], (rect[1][1], rect[1][0]), rect[2] - 90)

    width, height = int(rect[1][0]), int(rect[1][1])

    src_pts = cv2.boxPoints(rect).astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    plate = cv2.warpPerspective(image, M, (width, height))
    ratio = plate.shape[1] / plate.shape[0]

    if MIN_RATIO < ratio < MAX_RATIO:
        src_pts = src_pts.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(image_rects, [src_pts], True, (0, 255, 0), 3)

    return plate


def _preproces_plate(plate: np.ndarray) -> np.ndarray:
    """
    Prepares plate image for text recognition

    plate: np.ndarray
        extracted plate

    returns: np.ndarray
        processed image
    """

    plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    plate = cv2.equalizeHist(plate)
    plate = cv2.medianBlur(plate, 3)

    return plate
