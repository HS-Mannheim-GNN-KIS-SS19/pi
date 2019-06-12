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
        DEFAULT = 5
        MAX = 180
        STEP_TIME = 0.015

    class HORIZONTAL:
        CHANNEL = 1
        MIN = 0
        DEFAULT = 21
        MAX = 125
        STEP_TIME = 0.015

    class VERTICAL:
        CHANNEL = 2
        MIN = 0
        MAX = 150
        DEFAULT = 129
        STEP_TIME = 0.02

    class CLUTCH:
        CHANNEL = 3
        MIN = 0
        MAX = 180
        DEFAULT = MAX - 30
        STEP_TIME = 0.02
        GRAB = MIN
        RELEASE = MAX


"""----------------------------------------IMAGE PROCESSING--------------------------------------------"""


class IMAGE_PROCESSING:
    MIN_RADIUS = 20
    X_OFFSET = -18
    EXECUTE_IN_PYTHON2 = False
    USE_IMAGE_NOT_CAMERA = False


"""----------------------------------------AI--------------------------------------------"""


def weights_path_by_qualname(qualname: str, cut: str) -> str:
    """

    :param qualname: classpath
    :param cut: string to be where a cut should be performed in qualname
    :return: str
    """
    return 'weights_of_{}.h5f'.format(
        str(qualname)[str(qualname).rfind(cut) + len(cut):].lower().replace(".", "_"))


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
    def __init__(self, weights_path: str, hidden_layer_sizes: [int], trainings: [TrainingPhase]):
        self.weights_path = weights_path
        self.trainings = trainings
        self.layers = hidden_layer_sizes


class Light:
    class Type(Enum):
        NATURAL = 0
        ARTIFICIAL = 1

    class Strength(Enum):
        LOW = 0
        HIGH = 1

    def __init__(self, lightning_type: Type.NATURAL or Type.ARTIFICIAL, strength: Strength.LOW or Strength.HIGH):
        self.type = lightning_type
        self.strength = strength

    def get_success_radius_by_grid_radius(self, input_grid_radius):
        return {
                   Light.Type.NATURAL: {
                       Light.Strength.LOW: 0.125,
                       Light.Strength.HIGH: 0.140
                   },
                   Light.Type.ARTIFICIAL: {
                       Light.Strength.LOW: 0.125,
                       Light.Strength.HIGH: 0.140
                   }
               }.get(self.type).get(self.strength) * input_grid_radius

    def get_color_space(self):
        return {
            Light.Type.NATURAL: {
                Light.Strength.LOW: [(100, 150, 0), (170, 500, 1000)],
                Light.Strength.HIGH: [(100, 150, 0), (130, 500, 1000)]
            },
            Light.Type.ARTIFICIAL: {
                Light.Strength.LOW: [(100, 50, 0), (170, 500, 1000)],
                Light.Strength.HIGH: [(100, 50, 0), (130, 500, 1000)]
            }
        }.get(self.type).get(self.strength)


class AiProperties:
    def __init__(self, network_properties: NetworkProperties, env_properties: EnvProperties,
                 reward_properties: RewardProperties, light: Light):
        self.network = network_properties  # type: NetworkProperties
        self.env = env_properties  # type: EnvProperties
        self.reward = reward_properties  # type: RewardProperties
        self.light = light


class SuccessRadiusByLightLevel:
    @classmethod
    def low(cls, input_grid_radius):
        return 0.18 * input_grid_radius

    @classmethod
    def medium(cls, input_grid_radius):
        return 0.24 * input_grid_radius

    @classmethod
    def high(cls, input_grid_radius):
        return 0.3 * input_grid_radius

    @classmethod
    def very_high(cls, input_grid_radius):
        return 0.4 * input_grid_radius


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
                            TrainingPhase(warm_up_steps=25, steps=60, epsilon=0.5,
                                          learn_rate=0.001),
                            TrainingPhase(warm_up_steps=1, steps=500, epsilon=0.3,
                                          learn_rate=0.001)
                        ]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=1000,
                                                 step_sizes=StepSize(base=4, vertical=20, horizontal=20)),
                    reward_properties=RewardProperties(for_failing=-300, for_success=10000,
                                                       state_multipliers=StateMultiplier(x=1, y=0, radius=10)),
                    light=Light(Light.Type.ARTIFICIAL, Light.Strength.HIGH))

        class OneServo:
            class V0:
                pass

    # Currently chosen properties
    properties = _Type.Simple.V0.properties  # type: AiProperties
