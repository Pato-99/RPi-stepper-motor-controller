## Python module for controlling stepper motors with Raspberry Pi

Designed for motor [**28BYJ-48** with **ULN2003**](https://rpishop.cz/motory-serva-a-cerpadla/1469-krokovy-motor-28byj-48-ridici-jednotka-sada.html)

Support for more motors and drivers will come in future...

### Contents
* [Usage](#usage)
* [Interface](#interface-of-28byj-48)
* [Plans for future](#plans-for-future)

### Usage

1. Place **motor.py** file in directory with script.
2. At the start of the script insert
   ```python
   from stepper import [motor you want] as motor
   ```
   * available motors: **28BYJ_48**
   * more soon...


### Interface

```python
__init__(self, motor_pins, pos_file='')
```
* motor_pins - tuple of 4 output pins from RPi (in order)
  
* pos_file - file where absolute position of motor is stored, so it can reload after each script run.
             Default '' means that the position will not be stored.
             If you enter name of file that does not exist, it will create one.
  


```python
turn_steps(self, n_steps, speed=0)
```
Turns n_steps

* n_steps - number of steps to turn. Direction is determined by the sign of n_steps.
  
* speed - desired speed in degrees per second. If set to 0 then default speed will be used.
  

```python
turn_angle(self, angle, speed=0, vebrose=False)
```
Turns by angle

* angle - number of degrees to turn. '+' is one direction '-' other.

* speed - speed - desired speed in degrees per second. If set to 0 then default speed will be used.

  
```python
step(self, direction)
```
  
Performs one step in desired direction

* direction - > 0 or < 0


```python
reset(self, sps=0, dps=0, absolute=False, vebrose=False)
``` 
Moves to initial position

* sps - speed in steps/second

* dps - speed in degrees/second

* absolute - if True it will move to absolute zero otherwise to relative zero
 
* vebrose - if True it will print to command prompt


```python
set_default_position(self)
```
Sets current position as default
  

```python
set_speed_sps(self, speed)
```
Sets default speed

* speed - desired speed in steps/second


```python
set_speed_dps(self, speed)
```
Sets default speed

* speed - desired speed in degrees/second
    

```python
release_pins(self)
```
Sets motor pins to low/0 to save power and prevent heating while left untouched for long time
  

```python
cleanup(self)
```
Saves absolute position to file if some was specified and clears the pins

* Use at the end of the script or when you do not plan to use the motor again
    
### Plans for future

* Add support for Nema 17 with A4988 driver
* Introduce acceleration methods
* Add support for radians
* One day, maybe universal package for controlling stepper motors...


### Notes

Rotation speed is always a bit lower than specified probably due to processor speed.
It can vary on different RPi versions.
