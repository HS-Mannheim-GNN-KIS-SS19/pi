from constants import AI, DEFAULT_SIMPLE_ENV_PROPERTIES
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv

PROPERTIES = AI.PROPERTIES.ENV_PROPERTIES


class SimpleEezybotEnv(AbstractEezybotEnv):
    """
        Moves 1 of 3 Servos having 2 possible Actions each (step backwards, step forward) every step

        Actionspace: 3 * 2 = 6
    """

    def _map_action_to_angle_offset_tuple(self):
        actions = []
        for i in range(PROPERTIES.STEP_RANGE):
            actions.append((-1 * i * PROPERTIES.STEP_SIZE_OF.BASE, 0, 0))
            actions.append((1 * i * PROPERTIES.STEP_SIZE_OF.BASE, 0, 0))
            actions.append((-1 * i * PROPERTIES.STEP_SIZE_OF.VERTICAL, 0, 0))
            actions.append((1 * i * PROPERTIES.STEP_SIZE_OF.VERTICAL, 0, 0))
            actions.append((-1 * i * PROPERTIES.STEP_SIZE_OF.HORIZONTAL, 0, 0))
            actions.append((1 * i * PROPERTIES.STEP_SIZE_OF.HORIZONTAL, 0, 0))
        return actions

    def __init__(self):
        # noinspection PyTypeChecker
        if not issubclass(PROPERTIES, DEFAULT_SIMPLE_ENV_PROPERTIES):
            raise TypeError("Current ENV Properties are not matching required Properties for SimpleEezybotEnv. "
                            "The Properties should extend or be SIMPLE_ENV_PROPERTIES")
        if PROPERTIES.ACTION_SPACE_SIZE != 6 * PROPERTIES.STEP_RANGE:
            raise TypeError(
                "Action Space is not matching. Current {}, Required: {}".format(PROPERTIES.ACTION_SPACE_SIZE,
                                                                                6 * PROPERTIES.STEP_RANGE))
        # noinspection PyTypeChecker
        AbstractEezybotEnv.__init__(self, PROPERTIES)
