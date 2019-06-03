"""----------------------------------------CONTROLLER--------------------------------------------"""
from abc import ABC

import numpy


class SERVO_CONTROLLER:
    USE_FAKE_CONTROLLER = False

    class STEP:
        SIZE = 1
        TIME = 0.02

    class MANUEL_CONTROL:
        STEP_SIZE = 5


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


class REWARD:
    DISTANCE_MULTIPLIER = 10
    RADIUS_MULTIPLIER = 60
    FOR_FAILING = -10


"""----------------------------------------ENV--------------------------------------------"""


class _I_ENV_PROPERTIES(ABC):
    """
        These Properties must be implemented in any Env Properties Class

        :not implemented: STEP_RANGE
        :not implemented: INPUT_GRID_RADIUS
        :not implemented: ACTION_SPACE_SIZE

    """
    INPUT_DATA_TYPE = NotImplemented  # type: numpy.int8 or numpy.int16 or numpy.int32 or numpy.float32 or numpy.float64
    INPUT_GRID_RADIUS = NotImplemented  # type: int
    ACTION_SPACE_SIZE = NotImplemented  # type: int


class _SHARED(_I_ENV_PROPERTIES, ABC):
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


class COMPLEX_ENV(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2 + 1
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE ** 3


class ONE_SERVO_ENV(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE


class SIMPLE_ENV(_SHARED):
    SINGLE_SERVO_ACTION_SPACE = _SHARED.STEP_RANGE * 2
    ACTION_SPACE_SIZE = SINGLE_SERVO_ACTION_SPACE * 3


"""----------------------------------------AI--------------------------------------------"""


class AI:
    class _AI_TYPES:
        class _I_AI_PROPERTIES(ABC):
            """
                These Properties must be implemented in any AI Properties Class
            """
            NAME = NotImplemented  # type: str
            PATH = NotImplemented  # type: str
            STEPS = NotImplemented  # type: int
            LEARN_RATE = NotImplemented  # type: float
            HIDDEN_LAYER_AMOUNT = NotImplemented  # type: int
            LAYER_SIZES = NotImplemented  # type: [int] # lenght: HIDDEN_LAYER_AMOUNT

        class _SHARED(_I_AI_PROPERTIES, ABC):
            """
                These Properties are shared among different AI's.
                AI Properties inheriting from this Class may override specific Properties
                AI Properties inheriting from this Class must override NAME, PATH, LAYERSIZES


                :not implemented: NAME
                :not implemented: PATH
                :not implemented: LAYERSIZES
            """
            STEPS = 100
            LEARN_RATE = 0.001
            HIDDEN_LAYER_AMOUNT = 3

        class BY_ENV:
            class Complex(_SHARED):
                NAME = "ComplexEezybotEnv-v0"
                PATH = 'dqn_{}_weights.h5f'.format(NAME)
                LAYER_SIZES = [16, 16, 16]

            class SIMPLE(_SHARED):
                NAME = "SimpleEezybotEnv-v0"
                PATH = 'dqn_{}_weights.h5f'.format(NAME)
                LAYER_SIZES = [16, 16, 16]

            class ONE_SERVO(_SHARED):
                NAME = "OneServoEezybotEnv-v0"
                PATH = 'dqn_{}_weights.h5f'.format(NAME)
                LAYER_SIZES = [8, 8, 8]

    # noinspection PyProtectedMember
    PROPERTIES = _AI_TYPES.BY_ENV.ONE_SERVO  # type: _AI_TYPES._I_AI_PROPERTIES
