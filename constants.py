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
    RESOLVE_REWARDS = False


class IMAGE_PROCESSING:
    USE_PYTHON_2 = False


class REWARD:
    DISTANCE_MULTIPLIER = 10
    RADIUS_MULTIPLIER = 60
    FOR_FAILING = -10


class ENV:
    STEP_RANGE = 1
    INPUT_RANGE = 10


class EEZYBOT_ENV:
    STEP_RANGE = ENV.STEP_RANGE
    SINGLE_SERVO_ACTION_SPACE = STEP_RANGE * 2 + 1
    ACTION_SPACE = SINGLE_SERVO_ACTION_SPACE ** 3
    INPUT_RANGE = ENV.INPUT_RANGE

    class STEP_SIZE_OF:
        BASE = 5
        VERTICAL = 10
        HORIZONTAL = 10


class ONE_SERVO_ENV:
    STEP_RANGE = ENV.STEP_RANGE
    SINGLE_SERVO_ACTION_SPACE = STEP_RANGE * 2
    ACTION_SPACE = SINGLE_SERVO_ACTION_SPACE
    INPUT_RANGE = ENV.INPUT_RANGE

    class STEP_SIZE_OF:
        BASE = 5


class SIMPLE_ENV:
    STEP_RANGE = ENV.STEP_RANGE
    SINGLE_SERVO_ACTION_SPACE = STEP_RANGE * 2
    ACTION_SPACE = SINGLE_SERVO_ACTION_SPACE * 3
    INPUT_RANGE = ENV.INPUT_RANGE

    class STEP_SIZE_OF:
        BASE = 5
        VERTICAL = 10
        HORIZONTAL = 10


class AI:
    class ENV_TYPE:
        Standart = "EezybotEnv-v0"
        SIMPLE = "SimpleEezybotEnv-v0"
        ONE_SERVO = "OneServoEezybotEnv-v0"

    ENV_NAME = ENV_TYPE.ONE_SERVO
    FILEPATH = 'dqn_{}_weights.h5f'.format(ENV_NAME)
    STEPS = 100
    LEARN_RATE = 0.001

    class LAYER_SIZE:
        FIRST = 8
        SECOND = 8
        THIRD = 8
