import json
from time import sleep

import cv2
from gpiozero import LED, DistanceSensor

from files_manager import remove_old_images
from ocr import read_text
from plates_recognition import find_plates

LAST_IMG = '/var/lib/motion/lastsnap.jpg'
SERVER_IMG = './server/static/output.png'
OUTPUT_IMG = './outputs/output.png'
OUTPUT_TEXT = './server/static/text.txt'

REMOVE_INTERVAL = 5.0
SLEEP_TIME = 2.0

distance_sensor = DistanceSensor(echo="BOARD7", trigger="BOARD8")
organge_led = LED("BOARD35")
white_led = LED("BOARD36")
red_led = LED("BOARD37")
blue_led = LED("BOARD38")


def main() -> None:
    """
    Main program function. It is responsible for execution of consecutive
    functions in the main loop. It also starts the second loop that removes
    old images from the 'motion' folder.
    """

    with open('./config.json', 'r') as file:
        config = json.load(file)

    remove_old_images(REMOVE_INTERVAL)

    while True:
        organge_led.on()
        white_led.off()
        print('[START]')

        if (image := cv2.imread(LAST_IMG)) is None:
            print('[NO IMAGE]')
            sleep(1)
            continue

        full_area = image.shape[0] * image.shape[1]
        plates = find_plates(image)

        if config['use_gpio']:
            sleep(SLEEP_TIME)
            read_text_flag = distance_sensor.distance < distance_sensor.threshold_distance
        else:
            read_text_flag = True

        for i, plate in enumerate(plates):
            ratio = plate.shape[1] / plate.shape[0]
            area = plate.shape[1] * plate.shape[0]

            if config['save_images']:
                cv2.imwrite(SERVER_IMG, plate)
                cv2.imwrite(OUTPUT_IMG, plate)

            if not read_text_flag:
                continue

            organge_led.off()
            white_led.on()

            if (text := read_text(plate)):
                blue_led.blink(on_time=2, off_time=0, n=1)
            else:
                red_led.blink(on_time=2, off_time=0, n=1)
                continue

            print(f'{"-" * 30}')
            print(f'| tesseract ({i+1}/{len(plates)})')
            print(f'| area: {area / full_area:.3f}, ratio: {ratio:.2f}')
            print(f'| text: "{text}"')

            with open(OUTPUT_TEXT, 'w') as file:
                file.write(text)

        print(f'{"-" * 30}')


if __name__ == '__main__':
    main()
