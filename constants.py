"""----------------------------------------CONTROLLER--------------------------------------------"""
from enum import Enum

import numpy


class SERVO_CONTROLLER:
    USE_FAKE_CONTROLLER = False


class EEZYBOT_CONTROLLER:
    class MANUEL_CONTROL:
        # Should be False if not running on pi due to use of picamera
        RESOLVE_REWARDS = True if not SERVO_CONTROLLER.USE_FAKE_CONTROLLER else False

    class BASE:
        CHANNEL = 0
        MIN = 0
        DEFAULT = 20
        MAX = 180
        STEP_SIZE = 2
        STEP_TIME = 0.02 * STEP_SIZE

    class HORIZONTAL:
        CHANNEL = 1
        MIN = 0
        DEFAULT = 21
        MAX = 125
        STEP_SIZE = 1
        STEP_TIME = 0.025 * STEP_SIZE

    class VERTICAL:
        CHANNEL = 2
        MIN = 0
        MAX = 150
        DEFAULT = 129
        STEP_SIZE = 1
        STEP_TIME = 0.02 * STEP_SIZE

    class CLUTCH:
        CHANNEL = 3
        MIN = 35
        MAX = 180
        DEFAULT = MAX - 30
        STEP_SIZE = 1
        STEP_TIME = 0.0075 * STEP_SIZE
        GRAB = MIN
        RELEASE = MAX


"""----------------------------------------IMAGE PROCESSING--------------------------------------------"""


class IMAGE_PROCESSING:
    MIN_RADIUS = 20
    X_OFFSET = -30
    EXECUTE_IN_PYTHON2 = False
    USE_IMAGE_NOT_CAMERA = False


"""----------------------------------------AI--------------------------------------------"""


def weights_path_by_qualname(qualname: str, cut: str) -> (str, int):
    """

    :param qualname: classpath
    :param cut: string to be where a cut should be performed in qualname
    :return: (str, int)
    """
    import os
    path = 'weights_of_{}/'.format(
        str(qualname)[str(qualname).rfind(cut) + len(cut):].lower().replace(".", "_"))
    cur = '0.h5f'
    try:
        for elem in os.listdir(path):
            if cur < elem:
                cur = elem
    except FileNotFoundError:
        os.makedirs(path)
    return path + '/', int(cur[0])


class TrainingPhase:
    def __init__(self, warm_up_steps: int, steps: int, epsilon: float, learn_rate: float):
        """

        :param warm_up_steps: steps at the beginning which collect experience and not learn anything
        :param steps: steps to be performed in training
        :param epsilon: Epsiolon of the EpsilonGreedyPolicy
        :param learn_rate
        """
        self.warm_up_steps = warm_up_steps
        self.steps = steps
        self.epsilon = epsilon
        self.learn_rate = learn_rate


class StateMultiplier:
    def __init__(self, x=1.0, y=1.0, radius=1.0):
        self.x = x
        self.y = y
        self.radius = radius


class RewardProperties:
    def __init__(self, for_failing: int, for_success: int, state_multipliers: StateMultiplier):
        """

        :param for_failing
        :param for_success
        :param state_multipliers: determines weight of each input, in the reward calculation
        """
        self.for_failing = (for_failing, for_failing, for_failing)
        self.for_success = (for_success, for_success, for_success)
        self.multiplier = state_multipliers


class StepSize:
    def __init__(self, base, vertical, horizontal):
        self.base = base
        self.vertical = vertical
        self.horizontal = horizontal


class EnvType:
    class Complex:
        name = "ComplexEezybotEnv-v0"
        action_space_size = 27

    class Simple:
        name = "SimpleEezybotEnv-v0"
        action_space_size = 6

    class One_servo:
        name = "OneServoEezybotEnv-v0"
        action_space_size = 2


class EnvProperties:
    def __init__(self, env_type: EnvType.Complex or EnvType.Simple or EnvType.One_servo,
                 input_data_type: numpy.int8 or numpy.int16 or numpy.int32 or numpy.float32 or numpy.float64,
                 input_grid_radius: int,
                 step_sizes: StepSize):
        """

        :param env_type
        :param input_data_type
        :param input_grid_radius
        :param step_sizes
        """
        self.type_name = env_type.name
        self.input_data_type = input_data_type
        self.input_grid_radius = input_grid_radius
        self.action_space_size = env_type.action_space_size
        self.step_size = step_sizes


class NetworkProperties:
    def __init__(self, weights_path: (str, int), hidden_layer_sizes: [int], trainings: [TrainingPhase]):
        self.weights_path = weights_path
        self.trainings = trainings
        self.layers = hidden_layer_sizes


class Light:
    class Intensity(float, Enum):
        VERY_LOW = 0.110
        LOW = 0.125
        MEDIUM = 0.140
        HIGH = 0.155
        VERY_HIGH = 0.17
        EXTREME = 0.2

    def __init__(self, intensity: Intensity):
        self.light_intensity = intensity

    def get_success_radius_by_grid_radius(self, input_grid_radius):
        return self.light_intensity.value * input_grid_radius

    def get_color_space(self):
        return {
            Light.Intensity.VERY_LOW: [(100, 50, 0), (170, 500, 1000)],
            Light.Intensity.LOW: [(100, 50, 0), (170, 500, 1000)],
            Light.Intensity.MEDIUM: [(100, 50, 0), (130, 500, 1000)],
            Light.Intensity.HIGH: [(100, 50, 0), (130, 500, 1000)],
            Light.Intensity.VERY_HIGH: [(100, 150, 0), (130, 500, 1000)],
            Light.Intensity.EXTREME: [(100, 150, 0), (130, 500, 1000)]

        }.get(self.light_intensity)


class AiProperties:
    def __init__(self, network_properties: NetworkProperties, env_properties: EnvProperties,
                 reward_properties: RewardProperties, light: Light, visualize: bool = False):
        self.network = network_properties  # type: NetworkProperties
        self.env = env_properties  # type: EnvProperties
        self.reward = reward_properties  # type: RewardProperties
        self.light = light
        self.visualize = visualize


class AI:
    class _Type:
        class Complex:
            class V0:
                pass

        class Simple:
            class V0:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[32, 32, 32],
                        trainings=[
                            # TrainingPhase(warm_up_steps=25, steps=60, epsilon=0.5,
                            #               learn_rate=0.001),
                            TrainingPhase(warm_up_steps=1, steps=500, epsilon=0.3,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=4, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=1, y=0, radius=10)),
                    light=Light(Light.Intensity.MEDIUM))

            class V1:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[32, 32, 32],
                        trainings=[
                            # TrainingPhase(warm_up_steps=25, steps=60, epsilon=0.5,
                            #               learn_rate=0.001),
                            TrainingPhase(warm_up_steps=1, steps=500, epsilon=0.3,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=4, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=1.3, y=0, radius=10)),
                    light=Light(Light.Intensity.LOW))

            class V2:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[500, 64, 64],
                        trainings=[
                            # TrainingPhase(warm_up_steps=40, steps=120, epsilon=0.5,
                            #               learn_rate=0.003),
                            # TrainingPhase(warm_up_steps=1, steps=250, epsilon=0.3,
                            #               learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=1, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=4, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=0, radius=10)),
                    light=Light(Light.Intensity.VERY_HIGH))

            class V3:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[500, 64, 64],
                        trainings=[
                            TrainingPhase(warm_up_steps=40, steps=150, epsilon=0.5,
                                          learn_rate=0.003),
                            TrainingPhase(warm_up_steps=1, steps=350, epsilon=0.35,
                                          learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=1, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=3, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=0, radius=10)),
                    light=Light(Light.Intensity.VERY_HIGH))

            class V4:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[500, 64, 64],
                        trainings=[
                            # TrainingPhase(warm_up_steps=40, steps=150, epsilon=0.5,
                            #              learn_rate=0.003),
                            # TrainingPhase(warm_up_steps=1, steps=350, epsilon=0.35,
                            #              learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=1, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=2, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=1, radius=20)),
                    light=Light(Light.Intensity.VERY_HIGH))

            class V5:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[64, 64, 64],
                        trainings=[
                            TrainingPhase(warm_up_steps=40, steps=150, epsilon=0.5,
                                          learn_rate=0.003),
                            TrainingPhase(warm_up_steps=1, steps=350, epsilon=0.35,
                                          learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=1, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=2, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=1, radius=20)),
                    light=Light(Light.Intensity.VERY_HIGH))

            class V6:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[128, 64, 64],
                        trainings=[
                            # TrainingPhase(warm_up_steps=40, steps=150, epsilon=0.5,
                            #             learn_rate=0.003),
                            # TrainingPhase(warm_up_steps=40, steps=700, epsilon=0.35,
                            #             learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=40, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=2, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=1, radius=20)),
                    light=Light(Light.Intensity.VERY_HIGH))

            class V7:
                properties = AiProperties(
                    network_properties=NetworkProperties(
                        weights_path=weights_path_by_qualname(__qualname__, cut="_Type."),
                        hidden_layer_sizes=[128, 64, 64],
                        trainings=[
                            TrainingPhase(warm_up_steps=40, steps=150, epsilon=0.5,
                                          learn_rate=0.003),
                            TrainingPhase(warm_up_steps=40, steps=700, epsilon=0.35,
                                          learn_rate=0.0015),
                            TrainingPhase(warm_up_steps=40, steps=300, epsilon=0.2,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=2, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=2, y=1, radius=20)),
                    light=Light(Light.Intensity.VERY_HIGH),
                    visualize=True)

        class OneServo:
            class V0:
                pass

    # Currently chosen properties
    properties = _Type.Simple.V7.properties  # type: AiProperties
