from argparse import ArgumentParser
from time import sleep

import cv2
from gpiozero import LED, DistanceSensor

from ocr import read_text
from plates_recognition import find_plates


LAST_IMG_OUT = './server/static/source.png'
PLATE_IMG = './server/static/output.png'
OUTPUT_TEXT = './server/static/text.txt'

SLEEP_TIME = 1.0

PLATES_DISTANCE_THR = 0.4
TEXT_DISTANCE_THR = 0.2


camera = cv2.VideoCapture(0)

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

    args = ArgumentParser()
    args.add_argument('--visual_mode', default=False, action='store_true')
    args.add_argument('--interactive_mode', default=False, action='store_true')
    args = args.parse_args()

    with open(OUTPUT_TEXT, 'w+') as file:
        file.write('')

    while True:
        organge_led.off()
        white_led.off()

        if args.visual_mode:
            sleep(SLEEP_TIME)
        
        print(f'{"-" * 30}')
        print('[START]')

        return_val, image = camera.read()
        if not return_val:
            print('[NO IMAGE]')
            continue

        if args.visual_mode:
            cv2.imwrite(LAST_IMG_OUT, image)

        if args.interactive_mode and distance_sensor.distance >= PLATES_DISTANCE_THR:
            continue

        organge_led.on()
        full_area = image.shape[0] * image.shape[1]
        plates = find_plates(image, args.visual_mode)

        for i, plate in enumerate(plates):
            ratio = plate.shape[1] / plate.shape[0]
            area = plate.shape[1] * plate.shape[0]

            if args.visual_mode:
                cv2.imwrite(PLATE_IMG, plate)

            if args.interactive_mode and distance_sensor.distance >= TEXT_DISTANCE_THR:
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'{"-" * 30}')
        print('[END]')
        del camera
