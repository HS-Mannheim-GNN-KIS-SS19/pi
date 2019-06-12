from time import sleep

from constants import EEZYBOT_CONTROLLER as EEZYBOT
from eezybot_controller import eezybot


def servo_test_max():
    eezybot.base.rotate_to(EEZYBOT.BASE.MAX)
    eezybot.verticalArm.rotate_to(EEZYBOT.VERTICAL.MAX)
    eezybot.horizontalArm.rotate_to(EEZYBOT.HORIZONTAL.MAX)
    eezybot.clutch.rotate_to(EEZYBOT.CLUTCH.MAX)


def servo_test_min():
    eezybot.base.rotate_to(EEZYBOT.BASE.MIN)
    eezybot.verticalArm.rotate_to(EEZYBOT.VERTICAL.MIN)
    eezybot.horizontalArm.rotate_to(EEZYBOT.HORIZONTAL.MIN)
    eezybot.clutch.rotate_to(EEZYBOT.CLUTCH.MIN)


def testBoth():
    eezybot.to_default()
    eezybot.wait_for_all()
    servo_test_max()
    eezybot.wait_for_all()
    servo_test_min()
    eezybot.wait_for_all()
    eezybot.to_default().wait_for_all()


eezybot.start().print_performed_rotations(True).activate_key_listener()
# testBoth()
print("ready")
sleep(10000)
