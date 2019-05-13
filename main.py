
from eezybot_servo_controller import eezybot
from gym_.gym_eezybot.envs.eezybot_env import Target
import ai_inerface

while True:
    ai_inerface.move_to(Target.MARBLE)
    eezybot.clutch.grab()
    ai_inerface.move_to(Target.DESTINATION)
    eezybot.clutch.release()
