from random import random
from time import sleep

from gpiozero import LED, DistanceSensor

organge_led = LED("BOARD35")
white_led = LED("BOARD36")
red_led = LED("BOARD37")
blue_led = LED("BOARD38")

distance_sensor = DistanceSensor(echo="BOARD7", trigger="BOARD8")


def reset_led():
    organge_led.on()
    white_led.off()
    red_led.off()
    blue_led.off()


def main() -> None:
    reset_led()

    while True:
        distance_sensor.wait_for_in_range()

        organge_led.off()
        white_led.on()

        sleep(2)
        white_led.off()

        if random() > 0.5:
            red_led.on()
        else:
            blue_led.on()

        sleep(2)
        reset_led()


if __name__ == '__main__':
    main()
