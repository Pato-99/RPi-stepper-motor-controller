#!/usr/bin/python3

import sys
from motor import *

motor_pins = [11, 13, 15, 16]
gp.setmode(gp.BOARD)

motor = Motor(motor_pins)


if len(sys.argv) == 2:
    motor.set_speed_dps(int(sys.argv[1]))



# --- interface for button control ---
gp.setup(36, gp.IN)
gp.setup(38, gp.IN)
gp.setup(40, gp.IN)

try:
    starting_step = 0
    last_direction = 1
    while True:
        if gp.input(36) and gp.input(38):
            time.sleep(0.5)
            while True:
                if gp.input(36):
                    motor.relase_pins()
                    time.sleep(0.5)
                    break
                motor.turn_steps(-1)

        if gp.input(36) and gp.input(40):
            time.sleep(0.5)
            while True:
                if gp.input(36):
                    motor.relase_pins()
                    time.sleep(0.5)
                    break
                motor.turn_steps(1)

        if gp.input(38):
            motor.turn_steps(-1)
            last_direction = -1

        if gp.input(40):
            motor.turn_steps(1)
            last_direction = 1

        if not gp.input(38) and not gp.input(40):
            motor.relase_pins()


except KeyboardInterrupt:
    motor.set_speed_dps(90)
    gp.cleanup([36, 38, 40])


