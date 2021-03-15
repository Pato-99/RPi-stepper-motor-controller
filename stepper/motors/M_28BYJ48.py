#!/usr/bin/python3

import RPi.GPIO as GP
import time
import numpy as np
import sys
from motor_interface import Motor


class M28BYJ48(Motor):
    _FULL_TURN = 512  # number of sequences needed for full turn
    _FULL_TURN_STEPS = 4096  # number of single half-steps for full turn
    _DEFAULT_SPS = 512  # default speed in steps per second
    _DEFAULT_DPS = 45  # default speed in degrees per second
    _DEFAULT_DELAY = 1 / 512  # default delay to match default speed

    # 1/8 of a turn half-steps
    _N_SEQUENCE = 8
    _SEQUENCE = ((1, 0, 0, 0),
                 (1, 1, 0, 0),
                 (0, 1, 0, 0),
                 (0, 1, 1, 0),
                 (0, 0, 1, 0),
                 (0, 0, 1, 1),
                 (0, 0, 0, 1),
                 (1, 0, 0, 1))

    def __init__(self, mtr_pins, pos_file=''):
        super().__init__(mtr_pins, pos_file)

        # loading speed
        self._delay = self._DEFAULT_DELAY
        self._sps = self._DEFAULT_SPS
        self._dps = self._DEFAULT_DPS

    # Turns rotor by specified number of steps
    # Direction is determined by the sign of steps
    #
    # If speed is not specified then instance speed is used.
    def turn_steps(self, steps, speed=0):
        direction = 1 if steps > 0 else -1
        if speed > 0:
            self.set_speed_sps(speed)

        for i in range(abs(steps)):
            self.step(direction)
            time.sleep(self._delay)

    # Turns rotor by specified angle in degrees with accuracy
    # +- one step that is 0.087890625 deg
    # Direction is determined by the sign of steps
    #
    # If speed is not specified then instance speed is used.
    def turn_angle(self, angle, speed=0, verbose=False):
        if verbose:
            print(f"Turning {angle} deg. Current position {self._pos_angle_relative} deg")

        if speed > 0:
            self.set_speed_dps(speed)

        # konstanta odchylky
        epsilon = np.finfo(float).eps * 1000
        diff_steps = 0

        steps = self._degrees_to_steps(angle)
        diff_up = steps - np.floor(steps)
        diff_down = steps - np.ceil(steps)

        # je presnejsi udelat o krok vice nebo mene?
        if diff_up < abs(diff_down):
            self._STEP_DIFF += diff_up
            steps = int(np.floor(steps))
        else:
            self._STEP_DIFF += diff_down
            steps = int(np.ceil(steps))

        # ma se pridat ci odebrat krok? - na zaklade celkoveho offsetu
        if self._STEP_DIFF > 1 - epsilon:
            diff_steps = 1
            self._STEP_DIFF -= 1
        if self._STEP_DIFF < -1 + epsilon:
            diff_steps = -1
            self._STEP_DIFF += 1

        # kdyz se celkovy offset blizi 0, nastav ho na 0
        if epsilon * 10 > self._STEP_DIFF > epsilon * -10:
            self._STEP_DIFF = 0

        # proved otoceni
        self.turn_steps(steps + diff_steps)

    # Moves rotor to initial position
    # Relative or absolute
    def reset(self, sps=0, dps=0, absolute=False, verbose=False):
        if verbose and absolute:
            print(f"Resetting to absolute 0 from:\n\t{self._pos_absolute} steps\n\t{self._pos_angle_absolute} deg")
        if verbose and not absolute:
            print(f"Resetting to relative 0 from:\n\t{self._pos_relative} steps\n\t{self._pos_angle_relative} deg")

        if dps > 0:
            self.set_speed_dps(dps)
        if sps > 0:
            self.set_speed_sps(sps)

        if not absolute:
            direction = -1 if self._pos_relative < self._FULL_TURN_STEPS / 2 else 1
            while self._pos_relative != 0:
                self.step(direction)
                time.sleep(self._delay)
        else:
            direction = 1 if self._pos_absolute < 0 else -1
            while self._pos_absolute != 0:
                self.step(direction)
                time.sleep(self._delay)
            self._pos_relative = 0
            self._pos_angle_relative = 0
        self.release_pins()

        if verbose and absolute:
            print(f"Done, absolute position:\n\t{self._pos_absolute} steps\n\t{self._pos_angle_absolute} deg")
        if verbose and not absolute:
            print(f"Done, relative position:\n\t{self._pos_relative} steps\n\t{self._pos_angle_relative} deg")

    @staticmethod
    def _degrees_to_steps(deg):
        return deg / 360 * 4096

    @staticmethod
    def _steps_to_degrees(steps):
        return steps / 4096 * 360


if __name__ == "__main__":
    motor_pins = [11, 13, 15, 16]
    GP.setmode(GP.BOARD)

    motor = M28BYJ48(motor_pins)

    if len(sys.argv) == 3:
        motor.set_speed_dps(int(sys.argv[2]))
        motor.turn_angle(1, int(sys.argv[1]))
    else:
        motor.cleanup()
        exit(1)
    motor.cleanup()
