"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""
import time
from adafruit_servokit import ServoKit

# 0: drehen
# 1: links
# 2: rechts
# 3: greifer
# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.


kit = ServoKit(channels=8)


def reset():
    kit.servo[0].angle = 0
    kit.servo[1].angle = 0
    kit.servo[2].angle = 0
    kit.servo[3].angle = 45


def standard_servo_test():
    kit.servo[2].angle = 180
    time.sleep(2)
    kit.servo[2].angle = 0
    time.sleep(2)
    kit.servo[2].angle = 180
    time.sleep(2)
    reset()


standart_servo_test()

# für greifen
# kit.servo[3].angle = 35
