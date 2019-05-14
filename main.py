
from eezybot_servo_controller import eezybot
import ai_inerface

while True:
    ai_inerface.go_to_marble()
    eezybot.clutch.grab()
    ai_inerface.go_to_destination()
    eezybot.clutch.release()
