#!/usr/bin/python3

import RPi.GPIO as gp
import time
import numpy as np
import sys


# "28BYJ-48"
class Motor:
    FULL_TURN = 512  # number of sequences needed for full turn
    FULL_TURN_STEPS = 4096  # number of single half-steps for full turn
    DEFAULT_SPS = 512  # default speed in steps per second
    DEFAULT_DPS = 45  # default speed in degrees per second
    DEFAULT_DELAY = 1 / 512  # default delay to match default speed

    # 1/8 of a turn half-steps
    N_SEQUENCE = 8
    SEQUENCE = ((1, 0, 0, 0),
                (1, 1, 0, 0),
                (0, 1, 0, 0),
                (0, 1, 1, 0),
                (0, 0, 1, 0),
                (0, 0, 1, 1),
                (0, 0, 0, 1),
                (1, 0, 0, 1))

    def __init__(self, motor_pins, pos_file=None):
        # setting up pins
        self.motor_pins = motor_pins
        for pin in self.motor_pins:
            gp.setup(pin, gp.OUT)
            gp.output(pin, 0)


        # setting relative position to 0
        self.pos_relative = 0
        self.pos_angle_relative = 0

        # loading position
        self.pos_file = pos_file
        try:
            with open(pos_file, "r") as rot:
                self.pos_absolute = int(rot.read())
            self.pos_angle_absolute = self.steps_to_degrees(self.pos_absolute)
        except FileNotFoundError:
            self.pos_absolute = 0
            self.pos_angle_absolute = 0

        # loading speed
        self.delay = self.DEFAULT_DELAY
        self.sps = self.DEFAULT_SPS
        self.dps = self.DEFAULT_DPS

        # diff counter for turning in angles
        self.STEP_DIFF = 0

    def __str__(self):
        return f"Absolute position: {self.pos_angle_absolute} deg\nRelative position: {self.pos_angle_relative} deg"

    '''
    Turns rotor by specified number of steps
    Direction is determined by the sign of steps
    
    If speed is not specified then instance speed is used.
    '''

    def turn_steps(self, steps, speed=0):
        direction = 1 if steps > 0 else -1
        if speed > 0:
            self.set_speed_sps(speed)

        for i in range(abs(steps)):
            self.step(direction)
            time.sleep(self.delay)

    '''
    Turns rotor by specified angle in degrees with accuracy 
    +- one step that is 0.087890625 deg
    Direction is determined by the sign of steps
    
    If speed is not specified then instance speed is used.
    '''

    def turn_angle(self, angle, speed=0, vebrose=False):
        if vebrose:
            print(f"Turning {angle} deg. Current position {self.pos_angle_relative} deg")

        if speed > 0:
            self.set_speed_dps(speed)

        # konstanta odchylky
        epsilon = np.finfo(float).eps * 1000
        diff_steps = 0

        steps = self.degrees_to_steps(angle)
        diff_up = steps - np.floor(steps)
        diff_down = steps - np.ceil(steps)

        # je presnejsi udelat o krok vice nebo mene?
        if diff_up < abs(diff_down):
            self.STEP_DIFF += diff_up
            steps = int(np.floor(steps))
        else:
            self.STEP_DIFF += diff_down
            steps = int(np.ceil(steps))

        # ma se pridat ci odebrat krok? - na zaklade celkoveho offsetu
        if self.STEP_DIFF > 1 - epsilon:
            diff_steps = 1
            self.STEP_DIFF -= 1
        if self.STEP_DIFF < -1 + epsilon:
            diff_steps = -1
            self.STEP_DIFF += 1

        # kdyz se celkovy offset blizi 0, nastav ho na 0
        if epsilon * 10 > self.STEP_DIFF > epsilon * -10:
            self.STEP_DIFF = 0

        # proved otoceni
        self.turn_steps(steps + diff_steps)

    '''
    Sets motor_pins to state described by tuple
    '''

    def set_pins(self, state):
        for pin, st in zip(self.motor_pins, state):
            gp.output(pin, st)

    '''
    Does one step in specificated direction
    '''

    def step(self, direction):
        # update absolute positions
        self.pos_absolute += direction
        self.pos_angle_absolute = self.steps_to_degrees(self.pos_absolute)

        # update relative positions
        self.pos_relative = (self.pos_relative + direction) % self.FULL_TURN_STEPS
        self.pos_angle_relative = self.steps_to_degrees(self.pos_relative)

        # do step
        self.set_pins(self.SEQUENCE[self.pos_relative % self.N_SEQUENCE])

    '''
    Moves rotor to initial position
    
    Relative or absolute
    '''

    def reset(self, absolute=False, vebrose=False):
        if vebrose and absolute:
            print(f"Resetting to absolute 0 from:\n\t{self.pos_absolute} steps\n\t{self.pos_angle_absolute} deg")
        if vebrose and not absolute:
            print(f"Resetting to relative 0 from:\n\t{self.pos_relative} steps\n\t{self.pos_angle_relative} deg")

        if not absolute:
            direction = -1 if self.pos_relative < self.FULL_TURN_STEPS / 2 else 1
            while self.pos_relative != 0:
                self.step(direction)
                time.sleep(self.delay)
        else:
            direction = 1 if self.pos_absolute < 0 else -1
            while self.pos_absolute != 0:
                self.step(direction)
                time.sleep(self.delay)
            self.pos_relative = 0
            self.pos_angle_relative = 0
        self.relase_pins()

        if vebrose and absolute:
            print(f"Done, absolute position:\n\t{self.pos_absolute} steps\n\t{self.pos_angle_absolute} deg")
        if vebrose and not absolute:
            print(f"Done, relative position:\n\t{self.pos_relative} steps\n\t{self.pos_angle_relative} deg")

    '''
    Sets current position as initial
    '''

    def set_default_position(self):
        self.pos_absolute = 0
        self.pos_angle_absolute = 0
        self.pos_relative = 0
        self.pos_angle_relative = 0

    @staticmethod
    def degrees_to_steps(deg):
        return deg / 360 * 4096

    @staticmethod
    def steps_to_degrees(steps):
        return steps / 4096 * 360

    def set_speed_dps(self, speed):
        self.dps = speed
        self.delay = 1 / self.degrees_to_steps(speed)
        self.sps = 1 / self.delay

    def set_speed_sps(self, speed):
        self.sps = speed
        self.delay = 1 / speed
        self.dps = self.steps_to_degrees(self.sps)

    '''
    Sets output to 0 for each motor pin
    '''

    def relase_pins(self):
        for pin in self.motor_pins:
            gp.output(pin, 0)

    '''
    Unsets motor pins and saves position
    '''

    def cleanup(self):
        self.relase_pins()
        for pin in self.motor_pins:
            gp.cleanup(pin)

        if self.pos_file:
            with open(pos_file, "w") as rot:
                rot.write(str(self.pos_absolute))


if __name__ == "__main__":
    motor_pins = [11, 13, 15, 16]
    gp.setmode(gp.BOARD)

    motor = Motor(motor_pins)

    if len(sys.argv) == 3:
        motor.set_speed_dps(int(sys.argv[2]))
        motor.turn_angle(1, int(sys.argv[1]))
    else:
        motor.cleanup()
        exit(1)

    gp.cleanup()
