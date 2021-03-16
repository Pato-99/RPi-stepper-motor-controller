import RPi.GPIO as GP
import numpy as np
import time


class Motor:
    _FULL_TURN_STEPS = None
    _DEFAULT_SPS = None  # default speed in steps per second
    _DEFAULT_DPS = None  # default speed in degrees per second
    _DEFAULT_DELAY = None  # default delay to match default speed
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

        # loading speed
        self._delay = self._DEFAULT_DELAY
        self._sps = self._DEFAULT_SPS
        self._dps = self._DEFAULT_DPS

    def __str__(self):
        return f"Absolute position: {self._pos_angle_absolute} deg\nRelative position: {self._pos_angle_relative} deg\n" \
               f"Speed: {self._sps}"

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

    def _degrees_to_steps(self, deg):
        return deg / 360 * self._FULL_TURN_STEPS

    def _steps_to_degrees(self, steps):
        return steps / self._FULL_TURN_STEPS * 360
