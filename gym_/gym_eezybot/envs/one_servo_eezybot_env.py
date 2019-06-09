from constants import AI
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv

env_properties = AI.properties.env


class OneServoEezybotEnv(AbstractEezybotEnv):
    """
        Moves the Base Servo wich has 2 possible Actions (step backwards, step forward) every step

        Actionspace: 1 * 2 = 2
    """

    def _map_action_to_angle_offset_tuple(self):
        return [(0, 0, -env_properties.step_size.horizontal),
                (0, 0, env_properties.step_size.horizontal)]


def __init__(self):
    if env_properties.action_space_size != 2:
        raise TypeError(
            "Action Space is not matching. Current {}, Required: {}".format(env_properties.action_space_size, 2))
    AbstractEezybotEnv.__init__(self, env_properties)
