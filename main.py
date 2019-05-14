
from eezybot_servo_controller import eezybot
import ai_interface

while True:
    ai_interface.go_to_marble()
    eezybot.clutch.grab()
    ai_interface.go_to_destination()
    eezybot.clutch.release()
