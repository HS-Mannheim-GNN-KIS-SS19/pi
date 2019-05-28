USE_FAKE_CONTROLLER = False


# TODO min, max werte auf -1 bis 1 umstellen oder so
# makes no sense since obviously 0 is min and 1 is max.
# Another constant for default giving the relative value (between 0 and 1) would make sense.
class STEP:
    SIZE = 1
    TIME = 0.02


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
    STEP = 5


class IMAGE_PROCESSING:
    use_python_2 = False


class ENV:
    STEP_RANGE = 1
    SINGLE_SERVO_ACTION_SPACE = STEP_RANGE * 2 + 1
    ACTION_SPACE = (STEP_RANGE * 2 + 1) ** 3
    D_REWARD_MULTIPLIER = 10
    R_REWARD_MULTIPLIER = 60

    class STEP_SIZE_OF:
        BASE = 5
        VERTICAL = 10
        HORIZONTAL = 10


class AI:
    ENV_NAME = 'EezybotEnv-v0'
    FILEPATH = 'dqn_{}_weights.h5f'.format(ENV_NAME)
    STEPS = 100
    LEARN_RATE = 0.001

    class LAYER_SIZE:
        FIRST = 64
        SECOND = 64
        THIRD = 64
