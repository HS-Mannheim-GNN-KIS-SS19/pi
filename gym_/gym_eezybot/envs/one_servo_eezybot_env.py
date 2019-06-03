from constants import ONE_SERVO_ENV
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv


class OneServoEezybotEnv(AbstractEezybotEnv):
    """
        Moves the Base Servo wich has 2 possible Actions (step backwards, step forward) every step

        Actionspace: 1 * 2 = 2
    """

    def _map_action_to_angle_offsets_tuple(self):
        actions = []
        for i in range(ONE_SERVO_ENV.STEP_RANGE):
            actions.append((-1 * i * ONE_SERVO_ENV.STEP_SIZE_OF.BASE, 0, 0))
            actions.append((1 * i * ONE_SERVO_ENV.STEP_SIZE_OF.BASE, 0, 0))
        return actions

    def __init__(self):
        # noinspection PyTypeChecker
        AbstractEezybotEnv.__init__(self, ONE_SERVO_ENV)
