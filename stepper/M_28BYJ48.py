from stepper.motor_interface import Motor


class M28BYJ48(Motor):
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
