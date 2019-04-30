import multiprocessing.pool
import threading
import time
import adafruit_servokit
import sys

_BASE_CHANNEL = 0
_ARM_VERTICAL_CHANNEL = 1
_ARM_HORIZONTAL_CHANNEL = 2
_CLUTCH_CHANNEL = 3

_STEP_SIZE = 0.5
_STEP_TIME = 0.005

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
_kit = adafruit_servokit.ServoKit(channels=8)

pool = multiprocessing.pool.ThreadPool()


class _Servo:

    # prevents basic class from direct instantiation.
    def __new__(cls, *args, **kwargs):
        if cls is _Servo:
            raise TypeError("base class may not be instantiated")
        return object.__new__(cls)

    def __init__(self, channel_number):
        _IS_PI2 = sys.version_info < (3, 0)
        if _IS_PI2:
            from Queue import Queue
        else:
            from queue import Queue

        self.__channel_number = channel_number
        self.__interrupted = False
        self.__queue = Queue()
        threading.Thread(target=self.__rotation_control, daemon=True).start()

    # adds rotation to queue and waits for all queued rotations to be performed
    def rotate_and_wait(self, angle):
        self.rotate(angle)
        self.wait()

    def rotate(self, angle):
        self.__queue.put(angle)

    # runs permanently checking for new rotation requests
    def __rotation_control(self):
        while True:
            if self.__interrupted:
                self.__interrupted = False
                # For some reason the queue has no clear function.
                # Can't simply use new Queue because wait_for_rotations() function won't work that way
                while not self.__queue.empty():
                    self.__queue.get_nowait()
                    self.__queue.task_done()
            # waits for a new rotation request
            angle = self.__queue.get(block=True)
            self.__run_rotation(angle)
            self.__queue.task_done()

    def __run_rotation(self, angle):
        performed = None
        next_angle = _kit.servo[self.__channel_number].angle
        # calculate delta betwe      en current angle and destined angle
        delta = angle - _kit.servo[self.__channel_number].angle

        # divide delta in steps wich will be added on the current angle until the destined angle is reached
        # can be interrupted through interrupted flag
        # Each time, moving and waiting is performed in an additional Thread.
        # It calculates the next angle in the meantime and then waits for the movement to be finished
        for _ in range(int(abs(delta) / _STEP_SIZE)):
            if delta < 0:
                next_angle -= _STEP_SIZE
            else:
                next_angle += _STEP_SIZE
            if self.__interrupted:
                return
            if performed is not None:
                performed.wait()
            performed = pool.apply_async(self.__run_step, args=(next_angle,))
        if performed is not None:
            performed.wait()
        if (not self.__interrupted) and delta % _STEP_SIZE != 0:
            self.__run_step(angle)

    def __run_step(self, angle):
        _kit.servo[self.__channel_number].angle = angle
        time.sleep(_STEP_TIME)

    # waits until all rotations in the queue are performed
    def wait(self):
        self.__queue.join()

    # interrupts and clears all rotations
    def interrupt(self):
        self.__interrupted = True
        self.wait()

    def get_rotation(self):
        return _kit.servo[self.__channel_number].angle


class _Base(_Servo):
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if _Base.__instance is None:
            _Base()
        return _Base.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if _Base.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(_BASE_CHANNEL)
            _Base.__instance = self

    def reset(self, wait=True):
        if wait:
            self.rotate_and_wait(90)
        else:
            self.rotate(90)

    # rotations base to a point relative to the robot
    def rotate_to(self, x, y):
        from math import atan2, degrees

        alpha = degrees(atan2(y, x))
        degree = (alpha + 360) % 360

        # only possible if robot can rotation to negative degree
        if degree > 180:
            degree = -degree + 180
        self.rotate(degree)


class _ArmVertical(_Servo):
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if _ArmVertical.__instance is None:
            _ArmVertical()
        return _ArmVertical.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if _ArmVertical.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(_ARM_VERTICAL_CHANNEL)
            _ArmVertical.__instance = self

    def reset(self, wait=True):
        if wait:
            self.rotate_and_wait(75)
        else:
            self.rotate(75)


class _ArmHorizontal(_Servo):
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if _ArmHorizontal.__instance is None:
            _ArmHorizontal()
        return _ArmHorizontal.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if _ArmHorizontal.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(_ARM_HORIZONTAL_CHANNEL)
            _ArmHorizontal.__instance = self

    def reset(self, wait=True):
        if wait:
            self.rotate_and_wait(20)
        else:
            self.rotate(20)


class _Clutch(_Servo):
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if _Clutch.__instance is None:
            _Clutch()
        return _Clutch.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if _Clutch.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(_CLUTCH_CHANNEL)
            _Clutch.__instance = self

    def reset(self, wait=True):
        if wait:
            self.rotate_and_wait(45)
        else:
            self.rotate(45)

    def grab(self, wait=True):
        if wait:
            self.rotate_and_wait(35)
        else:
            self.rotate(35)


base = _Base()
armVertical = _ArmVertical()
armHorizontal = _ArmHorizontal()
clutch = _Clutch()


# interrupts and clears all rotations
def interrupt_all():
    base.interrupt()
    armVertical.interrupt()
    armHorizontal.interrupt()
    clutch.interrupt()


def wait_for_all():
    base.wait()
    armVertical.wait()
    armHorizontal.wait()
    clutch.wait()


def hard_reset():
    try:
        interrupt_all()
    finally:
        _kit.servo[_BASE_CHANNEL].angle = 90
        _kit.servo[_ARM_VERTICAL_CHANNEL].angle = 75
        _kit.servo[_ARM_HORIZONTAL_CHANNEL].angle = 20
        _kit.servo[_CLUTCH_CHANNEL].angle = 45


def reset(wait=True):
    base.reset(wait)
    armVertical.reset(wait)
    armHorizontal.reset(wait)
    clutch.reset(wait)


def key_listener():
    while True:
        def on_press(key):
            if str(key) == chr(27):
                interrupt_all()
                reset()
                sys.exit()

            if str(key) == 'q':
                base.rotate_and_wait(base.get_rotation() + 5)

            if str(key) == 'a':
                base.rotate_and_wait(base.get_rotation() - 5)

            if str(key) == 'w':
                armVertical.rotate_and_wait(armVertical.get_rotation() + 5)

            if str(key) == 's':
                armVertical.rotate_and_wait(armVertical.get_rotation() - 5)

            if str(key) == 'e':
                armHorizontal.rotate_and_wait(armHorizontal.get_rotation() + 5)

            if str(key) == 'd':
                armHorizontal.rotate_and_wait(armHorizontal.get_rotation() - 5)

            if str(key) == 'r':
                clutch.rotate_and_wait(clutch.get_rotation() + 5)

            if str(key) == 'f':
                clutch.rotate_and_wait(clutch.get_rotation() - 5)

        on_press(sys.stdin.read(1))
        time.sleep(0.1)


key_listener()
