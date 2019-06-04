"""----------------------------------------CONTROLLER--------------------------------------------"""
from abc import ABC

import numpy


class SERVO_CONTROLLER:
    USE_FAKE_CONTROLLER = True

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
        DEFAULT = 0
        MAX = 125

    class VERTICAL:
        CHANNEL = 2
        MIN = 0
        DEFAULT = 180
        MAX = 180

    class CLUTCH:
        CHANNEL = 3
        MIN = 0
        DEFAULT = 60
        MAX = 180
        GRAB = 35
        RELEASE = DEFAULT

    class MANUEL_CONTROL:
        RESOLVE_REWARDS = False


"""----------------------------------------REWARD--------------------------------------------"""


class DEFAULT_REWARD:
    DISTANCE_MULTIPLIER = 10
    RADIUS_MULTIPLIER = 60
    FOR_FAILING = -10


"""----------------------------------------ENV--------------------------------------------"""


class I_ENV_PROPERTIES(ABC):
    """
        These Properties must be implemented in any Env Properties Class

        :not implemented: STEP_RANGE
        :not implemented: INPUT_GRID_RADIUS
        :not implemented: ACTION_SPACE_SIZE

    """
    INPUT_DATA_TYPE = NotImplemented  # type: numpy.int8 or numpy.int16 or numpy.int32 or numpy.float32 or numpy.float64
    INPUT_GRID_RADIUS = NotImplemented  # type: int
    SINGLE_SERVO_ACTION_SPACE = NotImplemented  # type: int
    ACTION_SPACE_SIZE = NotImplemented  # type: int
    STEP_RANGE = NotImplemented  # type: int

    class STEP_SIZE_OF:
        BASE = NotImplemented  # type: int
        VERTICAL = NotImplemented  # type: int
        HORIZONTAL = NotImplemented  # type: int


class _SHARED(I_ENV_PROPERTIES, ABC):
    """
        These Properties are shared among different Env's.
        Env Properties inheriting from this Class may override specific Properties
        Env Properties inheriting from this Class must override ACTION_SPACE_SIZE

        :not implemented: ACTION_SPACE_SIZE
    """
    STEP_RANGE = 1
    INPUT_DATA_TYPE = numpy.int8
    INPUT_GRID_RADIUS = 10

    class STEP_SIZE_OF:
        BASE = 5
        VERTICAL = 10
        HORIZONTAL = 10


class DEFAULT_COMPLEX_ENV_PROPERTIES(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2 + 1
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE ** 3


class DEFAULT_ONE_SERVO_ENV_PROPERTIES(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE


class DEFAULT_SIMPLE_ENV_PROPERTIES(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE * 3


"""----------------------------------------AI--------------------------------------------"""


def weights_path_by_qualname(qualname, find):
    return 'weights_of_{}.h5f'.format(
        str(qualname)[str(qualname).rfind(find) + len(find) + 1:].lower().replace(".", "_"))


class I_AI_PROPERTIES(ABC):
    """
        These Properties must be implemented in any AI Properties Class
    """
    ENV_NAME = NotImplemented  # type: str
    WEIGHTS_PATH = NotImplemented  # type: str
    STEPS = NotImplemented  # type: int
    LEARN_RATE = NotImplemented  # type: float
    LAYER_SIZES = NotImplemented  # type: [int] # lenght: HIDDEN_LAYER_AMOUNT
    ENV_PROPERTIES = NotImplemented  # type: I_ENV_PROPERTIES

    class REWARD:
        DISTANCE_MULTIPLIER = NotImplemented  # type: int
        RADIUS_MULTIPLIER = NotImplemented  # type: int
        FOR_FAILING = NotImplemented  # type: int


class _SHARED_AI_PROPERTIES(I_AI_PROPERTIES, ABC):
    """
        These Properties are shared among different AI's.
        AI Properties inheriting from this Class may override specific Properties
        AI Properties inheriting from this Class must override NAME, PATH, LAYERSIZES, ENV_PROPERTIES


        :not implemented: NAME
        :not implemented: PATH
        :not implemented: LAYERSIZES
        :not implemented ENV_PROPERTIES
    """
    STEPS = 100
    LEARN_RATE = 0.001
    REWARD = DEFAULT_REWARD


class AI:
    class _AI_PROPERTIES_FOR:
        class COMPLEX:
            class V0(_SHARED_AI_PROPERTIES):
                ENV_NAME = "ComplexEezybotEnv-v0"
                WEIGHTS_PATH = weights_path_by_qualname(__qualname__, "BY_ENV")
                LAYER_SIZES = [16, 16, 16]
                ENV_PROPERTIES = DEFAULT_COMPLEX_ENV_PROPERTIES

        class SIMPLE:
            class V0(_SHARED_AI_PROPERTIES):
                ENV_NAME = "SimpleEezybotEnv-v0"
                WEIGHTS_PATH = weights_path_by_qualname(__qualname__, "BY_ENV")
                LAYER_SIZES = [16, 16, 16]
                ENV_PROPERTIES = DEFAULT_SIMPLE_ENV_PROPERTIES

        class ONE_SERVO:
            class V0(_SHARED_AI_PROPERTIES):
                ENV_NAME = "OneServoEezybotEnv-v0"
                WEIGHTS_PATH = weights_path_by_qualname(__qualname__, "BY_ENV")
                LAYER_SIZES = [8, 8, 8]
                ENV_PROPERTIES = DEFAULT_ONE_SERVO_ENV_PROPERTIES

    # noinspection PyProtectedMember
    PROPERTIES = _AI_PROPERTIES_FOR.ONE_SERVO.V0  # type: I_AI_PROPERTIES
