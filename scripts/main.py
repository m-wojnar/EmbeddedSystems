from time import sleep

import pytesseract

from files_manager import remove_old_images
from images_processing import extract_paper

REMOVE_INTERVAL = 5.0
SLEEP_TIME = 2.0


def main() -> None:
    """
    Main program function. It is responsible for execution of consecutive
    functions in the main loop. It also starts the second loop that removes
    old images from the 'motion' folder.
    """

    remove_old_images(REMOVE_INTERVAL)

    while True:
        if (image := extract_paper()) is None:
            continue

        if not (text := pytesseract.image_to_string(image).strip()):
            continue

        print(f'TEXT: "{text}"')
        sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
