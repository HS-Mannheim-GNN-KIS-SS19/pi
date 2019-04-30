import sys
import time

import eezybot


def servo_test():
    eezybot.reset()
    time.sleep(3)
    eezybot.base.rotate_and_wait(180)
    time.sleep(1)
    eezybot.armVertical.rotate_and_wait(180)
    time.sleep(1)
    eezybot.armHorizontal.rotate_and_wait(180)
    time.sleep(1)
    eezybot.clutch.grab()
    time.sleep(1)
    eezybot.reset()
    time.sleep(3)


try:
    servo_test()
finally:
    sys.exit(0)

# shoud rotate the base 90 degree
# eezybot.base.rotate_to(0, 1)
# eezybot.base.wait()
