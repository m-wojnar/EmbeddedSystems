import numpy as np
import cv2

MIN_AREA = 1000
MIN_RATIO = 4
MAX_RATIO = 5


def find_plates(image: np.ndarray) -> list[np.ndarray]:
    """
    Extracts licence plates images from given image

    image: np.ndarray
        image to process

    returns: list[np.ndarray]
        list of images with extraced plates
    """

    processed = _preprocess_image(image)
    segment_count, indexed, _, _ = cv2.connectedComponentsWithStats(
        processed, 8, cv2.CV_32S)

    plates = []

    for i in range(1, segment_count):
        segment = (indexed == i).astype('uint8') * 255
        area = np.sum(segment // 255)

        if area > MIN_AREA:
            plate = _crop_plate(segment, image)
            ratio = plate.shape[1] / plate.shape[0]

            if MIN_RATIO < ratio < MAX_RATIO:
                plate = _preproces_plate(plate)
                plates.append(plate)

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


def _crop_plate(segment: np.ndarray, image: np.ndarray) -> np.ndarray:
    """
    Extracts licence plates images from given image

    segment: np.ndarray
        selected segment

    image: np.ndarray
        original image

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
