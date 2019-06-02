from constants import SIMPLE_ENV
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv


class SimpleEezybotEnv(AbstractEezybotEnv):
    """
        Moves 1 of 3 Servos having 2 possible Actions each (step backwards, step forward) every step

        Actionspace: 3 * 2 = 6
    """

    def _get_action_space_size(self):
        return SIMPLE_ENV.ACTION_SPACE

    def _map_action_to_angle_offsets_tuple(self):
        actions = []
        for i in range(SIMPLE_ENV.STEP_RANGE):
            actions.append((-1 * i * SIMPLE_ENV.STEP_SIZE_OF.BASE, 0, 0))
            actions.append((1 * i * SIMPLE_ENV.STEP_SIZE_OF.BASE, 0, 0))
            actions.append((-1 * i * SIMPLE_ENV.STEP_SIZE_OF.VERTICAL, 0, 0))
            actions.append((1 * i * SIMPLE_ENV.STEP_SIZE_OF.VERTICAL, 0, 0))
            actions.append((-1 * i * SIMPLE_ENV.STEP_SIZE_OF.HORIZONTAL, 0, 0))
            actions.append((1 * i * SIMPLE_ENV.STEP_SIZE_OF.HORIZONTAL, 0, 0))
        return actions

    def __init__(self):
        AbstractEezybotEnv.__init__(self)
