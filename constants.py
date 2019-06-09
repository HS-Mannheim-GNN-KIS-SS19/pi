"""----------------------------------------CONTROLLER--------------------------------------------"""
from typing import Callable

import numpy


class SERVO_CONTROLLER:
    USE_FAKE_CONTROLLER = False

    class STEP:
        SIZE = 1
        TIME = 0.02

    class MANUEL_CONTROL:
        DEFAULT_STEP_SIZE = 5


class EEZYBOT_CONTROLLER:
    class BASE:
        CHANNEL = 0
        MIN = 0
        DEFAULT = 90
        MAX = 180

    class HORIZONTAL:
        CHANNEL = 1
        MIN = 0
        DEFAULT = 21
        MAX = 125

    class VERTICAL:
        CHANNEL = 2
        MIN = 0
        MAX = 150
        DEFAULT = 129

    class CLUTCH:
        CHANNEL = 3
        MIN = 0
        MAX = 180
        DEFAULT = MAX
        GRAB = MIN
        RELEASE = MAX

    class MANUEL_CONTROL:
        RESOLVE_REWARDS = True


"""----------------------------------------IMAGE PROCESSING--------------------------------------------"""


class ColorSpace:
    blue = [(195, 30, 0), (270, 100, 100)]


class IMAGE_PROCESSING:
    MIN_RADIUS = 20
    EXECUTE_IN_PYTHON2 = False
    USE_IMAGE_NOT_CAMERA = False


"""----------------------------------------AI--------------------------------------------"""


def weights_path_by_qualname(qualname, find):
    return 'weights_of_{}.h5f'.format(
        str(qualname)[str(qualname).rfind(find) + len(find) + 1:].lower().replace(".", "_"))


class TrainingPhase:
    def __init__(self, warm_up_steps: int, steps: int, epsilon: float, learn_rate: float):
        self.warm_up_steps = warm_up_steps
        self.steps = steps
        self.epsilon = epsilon
        self.learn_rate = learn_rate


class StateMultiplier:
    def __init__(self, x=1, y=1, radius=1):
        self.x = x
        self.y = y
        self.radius = radius


class RewardProperties:
    def __init__(self, for_failing: int, for_success: int, state_multipliers: StateMultiplier):
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
                 input_grid_radius: int, step_sizes: StepSize,
                 target_color_space: ColorSpace.blue,
                 check_for_success_func: Callable[[(int, int, int)], bool]):
        self.type_name = env_type.name
        self.input_data_type = input_data_type
        self.input_grid_radius = input_grid_radius
        self.target_color_space = target_color_space
        self.action_space_size = self.type_name.action_space_size
        self.step_size = step_sizes
        self.check_for_success_func = check_for_success_func


class NetworkProperties:
    def __init__(self, weights_path: str, hidden_layer_sizes: [int], trainings: [TrainingPhase]):
        self.weights_path = weights_path
        self.trainings = trainings
        self.layers = hidden_layer_sizes


class AiProperties:
    def __init__(self, network_properties: NetworkProperties, env_properties: EnvProperties,
                 reward_properties: RewardProperties):
        self.network = network_properties  # type: NetworkProperties
        self.env = env_properties  # type: EnvProperties
        self.reward = reward_properties  # type: RewardProperties


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
                        weights_path=weights_path_by_qualname(__qualname__, find="_Type"),
                        hidden_layer_sizes=[32, 32, 32],
                        trainings=[
                            TrainingPhase(warm_up_steps=40, steps=60, epsilon=0.6,
                                          learn_rate=0.01),
                            TrainingPhase(warm_up_steps=10, steps=100, epsilon=0.4,
                                          learn_rate=0.001),
                            TrainingPhase(warm_up_steps=10, steps=100, epsilon=0.2,
                                          learn_rate=0.001)]),
                    env_properties=EnvProperties(env_type=EnvType.Simple, input_data_type=numpy.int32,
                                                 input_grid_radius=10000,
                                                 target_color_space=ColorSpace.blue,
                                                 step_sizes=StepSize(base=5, vertical=20, horizontal=20),
                                                 check_for_success_func=lambda cur_state:
                                                 cur_state[2] > SuccessRadiusByLightLevel.high(1000)),
                    reward_properties=RewardProperties(for_failing=-1000, for_success=10000,
                                                       state_multipliers=StateMultiplier(radius=6)))

        class OneServo:
            class V0:
                pass

    properties = _Type.Simple.V0.properties  # type: AiProperties
