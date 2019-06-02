from constants import COMPLEX_ENV
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv


class ComplexEezybotEnv(AbstractEezybotEnv):
    """
        Moves 3 Servos having 3 possible Actions each (step backwards, stay, step forward) every step

        Actionspace: 3 ** 3 = 27
    """
    metadata = {'render.modes': ['human']}

    def _get_action_space_size(self):
        return COMPLEX_ENV.ACTION_SPACE

    def _map_action_to_angle_offsets_tuple(self):
        actions = []
        for base_angle in range(COMPLEX_ENV.SINGLE_SERVO_ACTION_SPACE):
            for arm_vertical_angle in range(COMPLEX_ENV.SINGLE_SERVO_ACTION_SPACE):
                for arm_horizontal_angle in range(COMPLEX_ENV.SINGLE_SERVO_ACTION_SPACE):
                    actions.append(
                        ((base_angle - COMPLEX_ENV.STEP_RANGE) * COMPLEX_ENV.STEP_SIZE_OF.BASE,
                         (arm_vertical_angle - COMPLEX_ENV.STEP_RANGE) * COMPLEX_ENV.STEP_SIZE_OF.VERTICAL,
                         (arm_horizontal_angle - COMPLEX_ENV.STEP_RANGE) * COMPLEX_ENV.STEP_SIZE_OF.HORIZONTAL))
        return actions

    def __init__(self):
        AbstractEezybotEnv.__init__(self)
