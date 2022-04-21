from time import sleep
import cv2

from files_manager import remove_old_images
from plates_recognition import find_plates
from ocr import read_text

LAST_IMG = '/var/lib/motion/lastsnap.jpg'
SERVER_IMG = './server/static/output.png'
OUTPUT_IMG = './outputs/output.png'
OUTPUT_TEXT = './server/static/text.txt'

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

        full_area = image.shape[0] * image.shape[1]
        plates = find_plates(image)

        for i, plate in enumerate(plates):
            ratio = plate.shape[1] / plate.shape[0]
            area = plate.shape[1] * plate.shape[0]
            
            if not (text := read_text(plate)):
                continue

            print(f'{"-" * 30}')
            print(f'| tesseract ({i+1}/{len(plates)})')
            print(f'| area: {area / full_area:.3f}, ratio: {ratio:.2f}')
            print(f'| text: "{text}"')

            cv2.imwrite(SERVER_IMG, plate)
            cv2.imwrite(OUTPUT_IMG, plate)

            with open(OUTPUT_TEXT, 'w') as file:
                file.write(text)

        print(f'{"-" * 30}')
        sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
