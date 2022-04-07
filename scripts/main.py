from time import sleep
import cv2

from files_manager import remove_old_images
from plates_recognition import find_plates
from ocr import read_text

LAST_IMG = '/var/lib/motion/lastsnap.jpg'
SERVER_IMG = './server/static/output.png'
OUTPUT_IMG = './outputs/output.png'

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
        print('[START]')

        if (image := cv2.imread(LAST_IMG)) is None:
            print('[NO IMAGE]')
            sleep(1)
            continue

        plates = find_plates(image)

        for i, plate in enumerate(plates):
            ratio = plate.shape[1] / plate.shape[0]
            area = plate.shape[1] * plate.shape[0]
            text = read_text(plate)

            print(f'{"-" * 30}')
            print(f'| tesseract ({i+1}/{len(plates)})')
            print(f'| area: {area}, ratio: {ratio:.2f}')
            print(f'| text: "{text}"')

            cv2.imwrite(SERVER_IMG, plate)
            cv2.imwrite(OUTPUT_IMG, plate)

        print(f'{"-" * 30}')
        sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
