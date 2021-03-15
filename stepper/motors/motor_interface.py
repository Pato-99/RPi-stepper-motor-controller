#!/usr/bin/python3

import RPi.GPIO as GP
from abc import ABC, abstractmethod


class Motor(ABC):
    _FULL_TURN_STEPS = None
    _N_SEQUENCE = None
    _SEQUENCE = None

    def __init__(self, mtr_pins, pos_file=''):
        # setting up pins
        self._motor_pins = mtr_pins
        for pin in self._motor_pins:
            GP.setup(pin, GP.OUT)
            GP.output(pin, 0)

        # initializing positions
        self._pos_relative = 0
        self._pos_angle_relative = 0
        self._pos_absolute = 0
        self._pos_angle_absolute = 0

        # try to load absolute position
        self.pos_file = pos_file
        if pos_file:
            try:
                with open(pos_file, "r") as rot:
                    self._pos_absolute = int(rot.read())
                self._pos_angle_absolute = self._steps_to_degrees(self._pos_absolute)
            except FileNotFoundError as e:
                print(e)
                self.cleanup()
                exit(1)

        # diff counter for turning in angles
        self._STEP_DIFF = 0

        # abstract attributes will be overridden in child
        self._delay = 0
        self._sps = 0
        self._dps = 0

    def __str__(self):
        return f"Absolute position: {self._pos_angle_absolute} deg\nRelative position: {self._pos_angle_relative} deg"

    @abstractmethod
    def turn_steps(self, n_steps, pos_file=''):
        pass

    @abstractmethod
    def turn_angle(self, angle, speed=0, verbose=False):
        pass

    # Does one step in specified direction
    def step(self, direction):
        # update absolute positions
        self._pos_absolute += direction
        self._pos_angle_absolute = self._steps_to_degrees(self._pos_absolute)

        # update relative positions
        self._pos_relative = (self._pos_relative + direction) % self._FULL_TURN_STEPS
        self._pos_angle_relative = self._steps_to_degrees(self._pos_relative)

        # do step
        self._set_pins(self._SEQUENCE[self._pos_relative % self._N_SEQUENCE])

    @abstractmethod
    def reset(self, sps=0, dps=0, absolute=False, verbose=False):
        pass

    # Sets current position as initial
    def set_default_position(self):
        self._pos_absolute = 0
        self._pos_angle_absolute = 0
        self._pos_relative = 0
        self._pos_angle_relative = 0

    def set_speed_sps(self, speed):
        self._sps = speed
        self._delay = 1 / speed
        self._dps = self._steps_to_degrees(self._sps)

    def set_speed_dps(self, speed):
        self._dps = speed
        self._delay = 1 / self._degrees_to_steps(speed)
        self._sps = 1 / self._delay

    # Sets output to 0 for each motor pin
    def release_pins(self):
        for pin in self._motor_pins:
            GP.output(pin, 0)

    # Unsets motor pins and saves position
    def cleanup(self):
        self.release_pins()
        for pin in self._motor_pins:
            GP.cleanup(pin)

        if self.pos_file:
            with open(self.pos_file, "w") as rot:
                rot.write(str(self._pos_absolute))

    # Sets motor_pins to state described by tuple
    def _set_pins(self, state):
        for pin, st in zip(self._motor_pins, state):
            GP.output(pin, st)

    @abstractmethod
    def _steps_to_degrees(self, steps):
        pass

    @abstractmethod
    def _degrees_to_steps(self, deg):
        pass
