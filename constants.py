USE_FAKE_CONTROLLER = False


class STEP_CONTROL:
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
    RELEASE = 70


class MANUEL_CONTROL:
    STEP = 5


class IMAGE_PROCESSING:
    use_python_2 = False


class ENV:
    ERROR_TOLERANCE = 1
    STEP_SIZE = 10
