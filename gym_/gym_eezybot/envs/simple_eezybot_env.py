from constants import AI
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv

env_properties = AI.properties.env


class SimpleEezybotEnv(AbstractEezybotEnv):
    """
        Moves 1 of 3 Servos having 2 possible Actions each (step backwards, step forward) every step

        Actionspace: 3 * 2 = 6
    """

    def _map_action_to_angle_offset_tuple(self):
        return [(-env_properties.step_size.base, 0, 0),
                (env_properties.step_size.base, 0, 0),
                (0, -env_properties.step_size.vertical, 0),
                (0, env_properties.step_size.vertical, 0),
                (0, 0, -env_properties.step_size.horizontal),
                (0, 0, env_properties.step_size.horizontal)]

    def __init__(self):
        if env_properties.action_space_size != 6:
            raise TypeError(
                "Action Space is not matching. Current {}, Required: {}".format(env_properties.action_space_size, 6))
        AbstractEezybotEnv.__init__(self, env_properties)
