#!/usr/bin/python3

from sys import argv
import RPi.GPIO as GP
import time
from motor import M_28BYJ_48 as MOTOR

motor_pins = [11, 13, 15, 16]
GP.setmode(GP.BOARD)

motor = MOTOR(motor_pins)

if len(argv) == 2:
    motor.set_speed_dps(int(argv[1]))

# --- interface for button control ---
GP.setup(36, GP.IN)
GP.setup(38, GP.IN)
GP.setup(40, GP.IN)

try:
    starting_step = 0
    last_direction = 1
    while True:
        if GP.input(36) and GP.input(38):
            time.sleep(0.5)
            while True:
                if GP.input(36):
                    motor.relase_pins()
                    time.sleep(0.5)
                    break
                motor.turn_steps(-1)

        if GP.input(36) and GP.input(40):
            time.sleep(0.5)
            while True:
                if GP.input(36):
                    motor.relase_pins()
                    time.sleep(0.5)
                    break
                motor.turn_steps(1)

        if GP.input(38):
            motor.turn_steps(-1)
            last_direction = -1

        if GP.input(40):
            motor.turn_steps(1)
            last_direction = 1

        if not GP.input(38) and not GP.input(40):
            motor.relase_pins()


except KeyboardInterrupt:
    print("Keyboard interrupt --> resetting position and quitting")
    motor.reset(dps=90)
    motor.cleanup()
    GP.cleanup([36, 38, 40])
