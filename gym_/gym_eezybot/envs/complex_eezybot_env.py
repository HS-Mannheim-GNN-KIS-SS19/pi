from constants import AI
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv

env_properties = AI.properties.env


class ComplexEezybotEnv(AbstractEezybotEnv):
    """
        Moves 3 Servos having 3 possible Actions each (step backwards, stay, step forward) every step

        Actionspace: 3 ** 3 = 27
    """

    def _map_action_to_angle_offset_tuple(self):
        actions = []
        for base_angle in range(3):
            for arm_vertical_angle in range(3):
                for arm_horizontal_angle in range(3):
                    actions.append(
                        ((base_angle - 1) * env_properties.step_size.base,
                         (arm_vertical_angle - 1) * env_properties.step_size.vertical,
                         (arm_horizontal_angle - 1) * env_properties.step_size.horizontal))
        return actions

    def __init__(self):
        if env_properties.action_space_size != 3 ** 3:
            raise TypeError(
                "Action Space is not matching. Current {}, Required: {}".format(env_properties.action_space_size,
                                                                                3 ** 3))
        AbstractEezybotEnv.__init__(self)
