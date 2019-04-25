import time
from adafruit_servokit import ServoKit

# 0: drehen
# 1: links
# 2: rechts
# 3: greifer
# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.


step_size = 1
step_speed = 1

kit = ServoKit(channels=8)


def reset():
    move(0, 0)
    move(1, 0)
    move(2, 0)
    move(3, 45)


def standard_servo_test():
    move(2, 180)
    time.sleep(2)
    move(2, 0)
    time.sleep(2)
    move(2, 180)
    time.sleep(2)
    reset()


def move(servo, angle):
    delta = abs(kit.servo[servo].angle - angle)
    for i in range(delta // step_size):
        if delta < 0:
            kit.servo[servo].angle = kit.servo[servo].angle - step_size
        else:
            kit.servo[servo].angle = kit.servo[servo].angle + step_size
        time.sleep(1 / step_speed)
    if delta % 2 == 1:
        kit.servo[servo].angle = kit.servo[servo].angle = angle
        time.sleep(1 / 2 * step_speed)

# für greifen
# kit.servo[3].angle = 35
