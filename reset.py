from __future__ import division

# Import the PCA9685 module.
import Adafruit_PCA9685

# Uncomment to enable debug output.
# import logging
# logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096
servo_mid = (int)((servo_min + servo_max) / 2)

# change accordingly
front_left = 1
front_right = 2
back_left = 3
back_right = 4
head = 0


def reset():
	pwm.set_pwm(head, 0, servo_mid)
	pwm.set_pwm(front_left, 0, servo_mid)
	pwm.set_pwm(front_right, 0, servo_mid)
	pwm.set_pwm(back_left, 0, servo_mid)
	pwm.set_pwm(back_right, 0, servo_mid)


# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

print('Reset.')
reset()
