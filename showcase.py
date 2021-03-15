#!/usr/bin/python3

from motor import *

def show_basic(motor):
    motor.turn_angle(180)
    motor.turn_angle(-180)

def show_stopping(motor):
    for i in range(6):
        motor.turn_angle(30, vebrose=True)
        time.sleep(0.5)

def show_bounce(motor):
    for i in range(5, 12):
        motor.turn_angle(3 * i, i * 10)
    for i in range(11, 5, -1):
        motor.turn_angle(-3 * i, i * 10)

def show_backing(motor):
    motor.set_speed_dps(60)
    motor.turn_angle(-60)
    motor.set_speed_dps(80)
    motor.turn_angle(20)

def show_acceleration(motor):
    for i in range(4, 12):
        motor.turn_angle(3 * i, i * 10)
    for i in range(11, 4, -1):
        motor.turn_angle(3 * i, i * 10)

def show_acceleration2(motor):
    for i in range(10, 120):
        motor.turn_angle(i / 10, i)
    for i in range(120, 10, -1):
        motor.turn_angle(i / 10, i)

def showcase(motor):
    show_basic(motor)

    show_stopping(motor)

    for i in range(2):
        show_bounce(motor)

    for i in range(2):
        show_acceleration(motor)

    for i in range(2):
        show_acceleration2(motor)

    for i in range(6):
        show_backing(motor)


# deprecated
def showcase2(motor):
    for i in range(2):
        motor.turn(1, 20, 50)
        # time.sleep(0.05)
        motor.turn(-1, 25, 60)
        # time.sleep(0.05)
        motor.turn(1, 30, 80)
        # time.sleep(0.05)
        motor.turn(-1, 35, 90)
        time.sleep(0.05)
        motor.turn(1, 20, 90)
        time.sleep(0.05)
        motor.turn(-1, 20, 90)
        time.sleep(0.05)

    for i in range(2):
        motor.turn(1, 30, 80)
        motor.turn(-1, 25, 60)
        motor.turn(1, 30, 80)
        motor.turn(-1, 25, 60)
        motor.turn(1, 20, 50)
        motor.turn(-1, 20, 50)
        motor.turn(-1, 20, 50)


if __name__ == "__main__":
    motor_pins = [11, 13, 15, 16]
    gp.setmode(gp.BOARD)
    motor = Motor(motor_pins)

    try:
        showcase(motor)
        motor.reset(vebrose=True)
    except KeyboardInterrupt:
        motor.reset()
        motor.cleanup()
        exit(1)

    motor.cleanup()

