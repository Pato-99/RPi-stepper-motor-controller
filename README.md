## Interface

* `__init__(self, motor_pins, pos_file='')`
* `turn_steps(self, n_steps, speed=0)`
* `turn_angle(self, angle, speed=0, vebrose=False)`
* `step(self, direction)`
* `reset(self, sps=0, dps=0, absolute=False, vebrose=False)`
* `set_default_position(self)`
* `set_speed_sps(self, speed)`
* `sed_speed_dps(self, speed)`
* `release_pins(self)`
* `cleanup`