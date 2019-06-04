from time import sleep

from constants import EEZYBOT_CONTROLLER as EEZYBOT
from eezybot_controller import eezybot


def servo_test_max():
    eezybot.base.rotate(EEZYBOT.BASE.MAX)
    eezybot.verticalArm.rotate(EEZYBOT.VERTICAL.MAX)
    eezybot.horizontalArm.rotate(EEZYBOT.HORIZONTAL.MAX)
    eezybot.clutch.rotate(EEZYBOT.CLUTCH.MAX)


def servo_test_min():
    eezybot.base.rotate(EEZYBOT.BASE.MIN)
    eezybot.verticalArm.rotate(EEZYBOT.VERTICAL.MIN)
    eezybot.horizontalArm.rotate(EEZYBOT.HORIZONTAL.MIN)
    eezybot.clutch.rotate(EEZYBOT.CLUTCH.MIN)


def testBoth():
    eezybot.to_default()
    eezybot.wait_for_all()
    servo_test_max()
    eezybot.wait_for_all()
    servo_test_min()
    eezybot.wait_for_all()
    eezybot.to_default().wait_for_all()


eezybot.start().print_performed_rotations(True).activate_key_listener()
print("ready")
sleep(10000)
