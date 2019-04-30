class _CHANNELS:
    BASE = 0
    VERTICAL = 1
    HORIZONTAL = 2
    CLUTCH = 3


class _STEP:
    SIZE = 0.5
    TIME = 0.005


class _MIN:
    SIZE = 0.5
    TIME = 0.005


class _DEFAULT:
    BASE = 0
    VERTICAL = 75
    HORIZONTAL = 20
    CLUTCH = 45


class _MAX:
    SIZE = 0.5
    TIME = 0.005


# makes private Classes importable.
# importing of private Classes prevents the pollution of namespace with Classes from Constants Module
__all__ = ['_CHANNELS', '_STEP', '_MIN', '_DEFAULT', '_MAX']
