import sys
import time

import eezybot


def servo_test():
    eezybot.reset()
    eezybot.base.rotate(180)
    time.sleep(1)
    eezybot.base.reset()
    eezybot.armVertical.rotate(180)
    time.sleep(1)
    eezybot.armVertical.reset()
    eezybot.armHorizontal.rotate(180)
    time.sleep(1)
    eezybot.armHorizontal.reset()
    eezybot.clutch.grab()
    time.sleep(1)
    eezybot.clutch.reset()
    time.sleep(3)


try:
    servo_test()
finally:
    eezybot.hard_reset()
    sys.exit(0)

# shoud rotate the base 90 degree
# eezybot.base.rotate_to(0, 1)
# eezybot.base.wait()
