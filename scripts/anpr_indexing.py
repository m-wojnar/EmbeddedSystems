import cv2
import pytesseract


def build_tesseract_options(psm=7):
    # tell Tesseract to only OCR alphanumeric characters
    alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    options = "-c tessedit_char_whitelist={}".format(alphanumeric)
    # set the PSM mode
    options += " --psm {}".format(psm)
    # return the built options string
    return options


def anpr(image, min_area=1000, min_AR=3, max_AR=6):
    # next, find regions in the image that are light
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
    light = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    cv2.imshow("Light Regions", light)
    cv2.waitKey(0)

    segment_count, indexed, stats, centroids = cv2.connectedComponentsWithStats(
        light, 8, cv2.CV_32S)

    plates = []

    for i in range(1, segment_count):
        segment = (indexed == i).astype('uint8')*255
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        cX, cY = centroids[i]

        if min_AR < w/float(h) < max_AR and area > min_area:
            output = image.copy()
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(output, (int(cX), int(cY)), 4, (0, 0, 255), -1)

            cv2.imshow("Output", output)
            cv2.imshow("Connected Component", segment)

            plates.append(cv2.medianBlur(cv2.equalizeHist(gray[y:y+h, x:x+w]), 3))
            cv2.imshow('plate', plates[-1])
            cv2.waitKey(0)

    recognized_texts = []
    if plates:
        options = build_tesseract_options()
        for i, plate in enumerate(plates):
            print(f'| tesseract ({i+1}/{len(plates)}) start |')
            text = pytesseract.image_to_string(plate, config=options)

            if text:
                recognized_texts.append(text)

            print(f'| tesseract ({i+1}/{len(plates)}) end   |')

    return recognized_texts


image = cv2.imread('license_plates/plate_1.jpg')
print(anpr(image))
