from time import sleep
from eezybotServoController import eezybot
from constants import *


def servo_test_max():
    eezybot.base.rotate(BASE.MAX)
    eezybot.verticalArm.rotate(VERTICAL.MAX)
    eezybot.horizontalArm.rotate(HORIZONTAL.MAX)
    eezybot.clutch.rotate(CLUTCH.MAX)


def servo_test_min():
    eezybot.base.rotate(BASE.MIN)
    eezybot.verticalArm.rotate(VERTICAL.MIN)
    eezybot.horizontalArm.rotate(HORIZONTAL.MIN)
    eezybot.clutch.rotate(CLUTCH.MIN)


def testBoth():
    eezybot.to_default().wait_for_all()
    servo_test_max()
    eezybot.wait_for_all()
    servo_test_min()


eezybot.start().print_performed_rotations(True).activate_key_listener()
print("ready")
sleep(10000)

# shoud rotate the base 90 degree
# eezybot.base.rotate_to(0, 1)
# eezybot.base.wait()
