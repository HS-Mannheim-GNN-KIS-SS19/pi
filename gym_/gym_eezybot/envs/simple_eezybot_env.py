from constants import SIMPLE_ENV
from gym_.gym_eezybot.envs import eezybot_env


class SimpleEezybotEnv(eezybot_env.EezybotEnv):

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
        super().__init__()
