from time import sleep
from eezybot_servo_controller import eezybot
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
    eezybot.to_default()
    eezybot.wait_for_all()
    servo_test_max()
    eezybot.wait_for_all()
    servo_test_min()


eezybot.start().print_performed_rotations(True).activate_key_listener()
#testBoth()
print("ready")
sleep(10000)

