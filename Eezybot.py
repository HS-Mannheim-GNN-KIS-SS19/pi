import time
from adafruit_servokit import ServoKit
from math import atan2, degrees

BASE_CHANNEL = 0
ARM_VERTICAL_CHANNEL = 1
ARM_HORIZONTAL_CHANNEL = 2
CLUTCH_CHANNEL = 3

STEP_SIZE = 1
STEP_TIME = 1

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=8)


class Servo():

    def __init__(self, channel_number):
        self.channel_number = channel_number

    def turn(self, angle):
        delta = angle - kit.servo[self.channel_number].angle
        for _ in range(int(abs(delta) / STEP_SIZE)):
            if delta < 0:
                kit.servo[self.channel_number].angle -= STEP_SIZE
            else:
                kit.servo[self.channel_number].angle += STEP_SIZE
            time.sleep(STEP_TIME)
        if delta % STEP_SIZE != 0:
            kit.servo[self.channel_number].angle = angle
            time.sleep(STEP_TIME)

    def reset(self):
        self.turn(0)


class Base(Servo):
    def __init__(self):
        super().__init__(BASE_CHANNEL)

    # turns base to a point relative to the robot
    def turn_to(self, x, y):
        alpha = degrees(atan2(y, x))
        degree = (alpha + 360) % 360

        # only possible if robot can turn to negative degree
        if degree > 180:
            degree = -degree + 180
        self.turn(degree)


class ArmVertical(Servo):
    def __init__(self):
        super().__init__(ARM_VERTICAL_CHANNEL)


class ArmHorizontal(Servo):
    def __init__(self):
        super().__init__(ARM_HORIZONTAL_CHANNEL)


class Clutch(Servo):
    def __init__(self):
        super().__init__(CLUTCH_CHANNEL)

    def reset(self):
        self.turn(45)

    def grab(self):
        self.turn(35)


base = Base()
armVertical = ArmVertical()
armHorizontal = ArmHorizontal()
clutch = Clutch()


def reset():
    base.reset()
    armVertical.reset()
    armHorizontal.reset()
    clutch.reset()


def servo_test():
    reset()
    base.turn(180)
    time.sleep(1)
    base.reset()
    armVertical.turn(180)
    time.sleep(1)
    armVertical.reset()
    armHorizontal.turn(180)
    time.sleep(1)
    armHorizontal.reset()
    clutch.grab()
    time.sleep(1)
    clutch.reset()


servo_test()

# shoud turn the base 90 degree
# base.turn_to(0, 1)

