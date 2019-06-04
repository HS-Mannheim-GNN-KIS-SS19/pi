from constants import AI, DEFAULT_COMPLEX_ENV_PROPERTIES
from gym_.gym_eezybot.envs.abstract_eezybot_env import AbstractEezybotEnv

PROPERTIES = AI.PROPERTIES.ENV_PROPERTIES


class ComplexEezybotEnv(AbstractEezybotEnv):
    """
        Moves 3 Servos having 3 possible Actions each (step backwards, stay, step forward) every step

        Actionspace: 3 ** 3 = 27
    """

    def _map_action_to_angle_offset_tuple(self):
        actions = []
        for base_angle in range(PROPERTIES.SINGLE_SERVO_ACTION_SPACE):
            for arm_vertical_angle in range(PROPERTIES.SINGLE_SERVO_ACTION_SPACE):
                for arm_horizontal_angle in range(PROPERTIES.SINGLE_SERVO_ACTION_SPACE):
                    actions.append(
                        ((base_angle - PROPERTIES.STEP_RANGE) * PROPERTIES.STEP_SIZE_OF.BASE,
                         (arm_vertical_angle - PROPERTIES.STEP_RANGE) * PROPERTIES.STEP_SIZE_OF.VERTICAL,
                         (arm_horizontal_angle - PROPERTIES.STEP_RANGE) * PROPERTIES.STEP_SIZE_OF.HORIZONTAL))
        return actions

    def __init__(self):
        # noinspection PyTypeChecker
        if not issubclass(PROPERTIES, DEFAULT_COMPLEX_ENV_PROPERTIES):
            raise TypeError("Current ENV Properties are not matching required Properties for SimpleEezybotEnv. "
                            "The Properties should extend or be COMPLEX_ENV_PROPERTIES")
        if PROPERTIES.SINGLE_SERVO_ACTION_SPACE != 1 + 2 * PROPERTIES.STEP_RANGE:
            raise TypeError(
                "Single Servo Action Space is not matching. Current {}, Required: {}".format(
                    PROPERTIES.SINGLE_SERVO_ACTION_SPACE, 1 + 2 * PROPERTIES.STEP_RANGE))
        if PROPERTIES.ACTION_SPACE_SIZE != (1 + 2 * PROPERTIES.STEP_RANGE) ** 3:
            raise TypeError(
                "Action Space is not matching. Current {}, Required: {}".format(PROPERTIES.ACTION_SPACE_SIZE,
                                                                                (1 + 2 * PROPERTIES.STEP_RANGE) ** 3))
        # noinspection PyTypeChecker
        AbstractEezybotEnv.__init__(self, PROPERTIES)
