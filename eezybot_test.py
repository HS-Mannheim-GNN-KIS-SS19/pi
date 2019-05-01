from time import sleep
from eezybotServoController import eezybot
from constants import *


def servo_test_max():
    eezybot.base.rotate(BASE.MAX).wait()
    eezybot.verticalArm.rotate(VERTICAL.MAX).wait()
    eezybot.horizontalArm.rotate(HORIZONTAL.MAX).wait()
    eezybot.clutch.rotate(CLUTCH.MAX).wait()


def servo_test_min():
    eezybot.base.rotate(BASE.MIN).wait()
    eezybot.verticalArm.rotate(VERTICAL.MIN).wait()
    eezybot.horizontalArm.rotate(HORIZONTAL.MIN).wait()
    eezybot.clutch.rotate(CLUTCH.MIN).wait()


def testBoth():
    eezybot.to_default().wait_for_all()
    servo_test_max()
    eezybot.wait_for_all()
    servo_test_min()


eezybot.start().print_performed_rotations(True).activate_key_listener()
testBoth()

# shoud rotate the base 90 degree
# eezybot.base.rotate_to(0, 1)
# eezybot.base.wait()
