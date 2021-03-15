#!/usr/bin/python3

import RPi.GPIO as GP
from M_28BYJ48 import M28BYJ48 as MOTOR
import time


def show_basic(mtr):
    mtr.turn_angle(180)
    mtr.turn_angle(-180)


def show_stopping(mtr):
    for i in range(6):
        mtr.turn_angle(30)
        time.sleep(0.5)


def show_bounce(mtr):
    for i in range(5, 12):
        mtr.turn_angle(3 * i, i * 10)
    for i in range(11, 5, -1):
        mtr.turn_angle(-3 * i, i * 10)


def show_backing(mtr):
    mtr.set_speed_dps(60)
    mtr.turn_angle(-60)
    mtr.set_speed_dps(80)
    mtr.turn_angle(20)


def show_acceleration(mtr):
    for i in range(4, 12):
        mtr.turn_angle(3 * i, i * 10)
    for i in range(11, 4, -1):
        mtr.turn_angle(3 * i, i * 10)


def show_acceleration2(mtr):
    for i in range(10, 120):
        mtr.turn_angle(i / 10, i)
    for i in range(120, 10, -1):
        mtr.turn_angle(i / 10, i)


def showcase(mtr):
    show_basic(mtr)

    show_stopping(mtr)

    for i in range(2):
        show_bounce(mtr)

    for i in range(2):
        show_acceleration(mtr)

    for i in range(2):
        show_acceleration2(mtr)

    for i in range(6):
        show_backing(mtr)


# old, do not use
def showcase2(mtr):
    for i in range(2):
        mtr.turn(1, 20, 50)
        # time.sleep(0.05)
        mtr.turn(-1, 25, 60)
        # time.sleep(0.05)
        mtr.turn(1, 30, 80)
        # time.sleep(0.05)
        mtr.turn(-1, 35, 90)
        time.sleep(0.05)
        mtr.turn(1, 20, 90)
        time.sleep(0.05)
        mtr.turn(-1, 20, 90)
        time.sleep(0.05)

    for i in range(2):
        mtr.turn(1, 30, 80)
        mtr.turn(-1, 25, 60)
        mtr.turn(1, 30, 80)
        mtr.turn(-1, 25, 60)
        mtr.turn(1, 20, 50)
        mtr.turn(-1, 20, 50)
        mtr.turn(-1, 20, 50)


if __name__ == "__main__":
    motor_pins = [11, 13, 15, 16]
    GP.setmode(GP.BOARD)
    motor = MOTOR(motor_pins)

    try:
        showcase(motor)
        motor.reset(verbose=True)
    except KeyboardInterrupt:
        motor.reset(dps=120)
        motor.cleanup()
        exit(1)

    motor.cleanup()
