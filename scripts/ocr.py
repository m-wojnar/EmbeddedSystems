import string
import numpy as np
import pytesseract


def read_text(image: np.ndarray) -> str:
    """
    Reads text from given image using tesseract OCR

    image: np.ndarray
        image to read text from

    returns: str
        text extracted from image
    """

    alphanumeric = string.ascii_uppercase + string.digits + ' '
    options = f'-c tessedit_char_whitelist={alphanumeric} --psm 7'

    text = pytesseract.image_to_string(image, config=options)
    return text.strip()
