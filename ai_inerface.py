from ai.ai import EezybotDQN
from eezybot_servo_controller import eezybot


def go_to_marble():
    EezybotDQN(eezybot.base)
    EezybotDQN(eezybot.verticalArm)
    EezybotDQN(eezybot.horizontalArm)
