import adafruit_servokit

_BASE_CHANNEL = 0
_ARM_VERTICAL_CHANNEL = 1
_ARM_HORIZONTAL_CHANNEL = 2
_CLUTCH_CHANNEL = 3



_kit = adafruit_servokit.ServoKit(channels=8)

_kit.servo[_BASE_CHANNEL].angle = 0
_kit.servo[_ARM_VERTICAL_CHANNEL].angle = 75
_kit.servo[_ARM_HORIZONTAL_CHANNEL].angle = 0
_kit.servo[_CLUTCH_CHANNEL].angle = 45
