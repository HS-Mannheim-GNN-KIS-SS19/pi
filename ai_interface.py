from ai.ai import EezybotDQN
from eezybot_controller import eezybot


def go_to_marble(train, create_new):
    EezybotDQN(train=train, create_new=create_new)


def go_to_destination():
    eezybot.base.rotate(0)
    eezybot.verticalArm.to_default()
    eezybot.horizontalArm.to_default()
    eezybot.start().finish_and_shutdown().wait_for_shutdown()
