import multiprocessing.pool
import threading
import time
import sys
import warnings
import constants as cons


import adafruit_servokit

# # Dummy Class for Testing
# class adafruit_servokit:
#     class ServoValue:
#         def __init__(self):
#             self.angle = 0
#
#     servo = [ServoValue(), ServoValue(), ServoValue(), ServoValue()]
#
#     @staticmethod
#     def ServoKit(channels=8):
#         return adafruit_servokit


# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
_kit = adafruit_servokit.ServoKit(channels=8)
_pool = None


class _Servo:

    # prevents basic class from direct instantiation.
    def __new__(cls, *args, **kwargs):
        if cls is _Servo:
            raise TypeError("base class may not be instantiated")
        return object.__new__(cls)

    def __init__(self, channel_number, min_degree, default_degree, max_degree):
        _IS_PI2 = sys.version_info < (3, 0)
        if _IS_PI2:
            from Queue import Queue
        else:
            from queue import Queue

        self.__min_degrees = min_degree
        self.__default_degree = default_degree
        self.__max_degrees = max_degree
        self.__channel_number = channel_number
        self.__rotation_controller_thread = None
        self.__queue = Queue()
        # Flags
        self.__print_rotations = False
        self.__clear_queue = False
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    def start(self):
        if self.__rotation_controller_thread is not None and self.__rotation_controller_thread.is_alive():
            raise AssertionError("Servo {) is already started".format(self.__class__.__name__[1:]))
        else:
            self.__rotation_controller_thread = threading.Thread(target=self.__rotation_control, daemon=True)
            self.__rotation_controller_thread.start()
        return self

    def _resolveDegree(self, value):
        return int(value * (self.__max_degrees - self.__min_degrees))

    # adds new Rotation to the queue.
    # Movement will be performed through the rotation controller calling the __run_rotation(angle) function
    def rotate(self, angle):
        if self.__block_rotate_method:
            raise AssertionError("Can not perform rotation to {}: Servo Controller is shutting down".format(angle))
        else:
            if angle < self.__min_degrees:
                raise AssertionError("Rotation out of Bounds: cur: {} < min: {}".format(angle, self.__min_degrees))
            elif angle < self.__min_degrees:
                raise AssertionError("Rotation out of Bounds: cur: {} > max: {}".format(angle, self.__max_degrees))
            else:
                self.__queue.put(angle)
        return self

    def rotate_relative(self, value):
        self.rotate(self._resolveDegree(value))
        return self

    # runs permanently checking for new rotation requests. Runs in new Thread after calling start() Function
    def __rotation_control(self):
        from queue import Empty
        while not self.__shutdown_rotation_controller:
            if self.__clear_queue:
                self.__clear_queue = False
                while not self.__queue.empty():
                    self.__queue.get_nowait()
                    self.__queue.task_done()
            # waits for a new rotation request
            try:
                angle = self.__queue.get(timeout=0.1)
                self.__run_rotation(angle)
                self.__queue.task_done()
            except Empty:
                pass

    def __run_rotation(self, angle):
        performed = None
        next_angle = _kit.servo[self.__channel_number].angle
        # calculate delta betwe      en current angle and destined angle
        delta = angle - _kit.servo[self.__channel_number].angle

        # divide delta in steps wich will be added on the current angle until the destined angle is reached
        # Each time, moving and waiting are performed in an additional Thread.
        # It calculates the next angle in the meantime and then waits for the movement and waiting to be finished
        for _ in range(int(abs(delta) / cons.STEP_CONTROL.SIZE)):
            if delta < 0:
                next_angle -= cons.STEP_CONTROL.SIZE
            else:
                next_angle += cons.STEP_CONTROL.SIZE
            if self.__clear_queue:
                return
            if performed is not None:
                performed.wait()
            performed = _pool.apply_async(self.__run_step, args=(next_angle,))
        if performed is not None:
            performed.wait()
        if (not self.__clear_queue) and delta % cons.STEP_CONTROL.SIZE != 0:
            self.__run_step(angle)
        if self.__print_rotations:
            print("servo {} performed movement to: {}".format(self.__class__.__name__[1:],
                                                              _kit.servo[self.__channel_number].angle))

    def __run_step(self, angle):
        _kit.servo[self.__channel_number].angle = angle
        time.sleep(cons.STEP_CONTROL.TIME)

    # waits until the rotation queue is empty
    def wait(self):
        if self.__rotation_controller_thread is None or not self.__rotation_controller_thread.is_alive():
            message = "Servo {} has not been started yet but still attempting to wait for rotations to be performed".format(
                self.__class__.__name__[1:])
            warnings.warn(message)
        self.__queue.join()
        return self

    # _clears and clears all rotations
    def clear_queue(self):
        self.__clear_queue = True
        return self

    # sets flag to prevents new rotations to be added to queue
    # then waits for the queue to be empty
    # finally sets flag to shutdown the rotation controller
    # if interrupt is true currently performed rotation as well as queued will be canceled.
    # if an value is given to final_rotation the last rotation before shutting down will be of this value
    def shutdown(self, final_rotation=None, interrupt=False):
        if self.__rotation_controller_thread is None or not self.__rotation_controller_thread.is_alive():
            raise AssertionError(
                "Servo {} wasn't running but tried to shut down".format(self.__class__.__name__[1:]))
        else:
            self.__block_rotate_method = True
            if interrupt:
                self.clear_queue()
            self.wait()
            if final_rotation is not None:
                self.__queue.put(final_rotation)
            self.wait()
            self.__shutdown_rotation_controller = True
            self.__rotation_controller_thread.join()
            self.__shutdown_rotation_controller = False
            self.__block_rotate_method = False
        return self

    def get_rotation(self):
        return _kit.servo[self.__channel_number].angle

    def print_performed_rotations(self, bool):
        self.__print_rotations = bool

    def to_default(self):
        self.rotate(self.__default_degree)
        return self


class _Base(_Servo):
    __instance = None

    def __init__(self):
        if _Base.__instance is not None:
            raise TypeError("This class is a singleton!")
        else:
            super().__init__(cons.BASE.CHANNEL, cons.BASE.MIN, cons.BASE.DEFAULT, cons.BASE.MAX)
            _Base.__instance = self

    # rotations base to a point relative to the robot
    def rotate_to(self, x, y):
        from math import atan2, degrees

        alpha = degrees(atan2(y, x))
        degree = (alpha + 360) % 360

        # only possible if robot can rotation to negative degree
        if degree > cons.BASE.MAX or degree < cons.BASE.MIN:
            raise AssertionError("servo can't turn to this point")
        self.rotate(degree)
        return self


class _ArmVertical(_Servo):
    __instance = None

    def __init__(self):
        if _ArmVertical.__instance is not None:
            raise TypeError("This class is a singleton!")
        else:
            super().__init__(cons.VERTICAL.CHANNEL, cons.VERTICAL.MIN, cons.VERTICAL.DEFAULT, cons.VERTICAL.MAX)
            _ArmVertical.__instance = self


class _ArmHorizontal(_Servo):
    __instance = None

    def __init__(self):
        if _ArmHorizontal.__instance is not None:
            raise TypeError("This class is a singleton!")
        else:
            super().__init__(cons.HORIZONTAL.CHANNEL, cons.HORIZONTAL.MIN, cons.HORIZONTAL.DEFAULT, cons.HORIZONTAL.MAX)
            _ArmHorizontal.__instance = self


class _Clutch(_Servo):
    __instance = None

    def __init__(self):
        if _Clutch.__instance is not None:
            raise TypeError("This class is a singleton!")
        else:
            super().__init__(cons.CLUTCH.CHANNEL, cons.CLUTCH.MAX, cons.CLUTCH.DEFAULT, cons.CLUTCH.MAX)
            _Clutch.__instance = self

    def grab(self):
        return self.rotate(cons.CLUTCH.GRAB)


class _Eezybot:
    __instance = None

    @staticmethod
    def getInstance():  # -> '_Eezybot':
        if _Eezybot.__instance is None:
            _Eezybot.__instance = _Eezybot()
        return _Eezybot.__instance

    def __init__(self):
        if _Eezybot.__instance is not None:
            raise TypeError("This class is a singleton!")
        self.__instance = self
        self.base = _Base()
        self.verticalArm = _ArmVertical()
        self.horizontalArm = _ArmHorizontal()
        self.clutch = _Clutch()
        self.is_running = False
        self.__key_listener_activated = False

    # interrupts and clears all rotations
    def clear_all_queues(self):
        self.base.clear_queue()
        self.verticalArm.clear_queue()
        self.horizontalArm.clear_queue()
        self.clutch.clear_queue()
        return self

    def wait_for_all(self):
        self.base.wait()
        self.verticalArm.wait()
        self.horizontalArm.wait()
        self.clutch.wait()
        return self

    def to_default(self):
        self.base.to_default()
        self.verticalArm.to_default()
        self.horizontalArm.to_default()
        self.clutch.to_default()
        return self

    def to_default_and_shutdown(self):
        return self.shutdown(base_angle=cons.BASE.DEFAULT, vertical_angle=cons.VERTICAL.DEFAULT,
                             horizontal_angle=cons.HORIZONTAL.DEFAULT,
                             clutch_angle=cons.CLUTCH.DEFAULT)

    def shutdown(self, base_angle=None, vertical_angle=None, horizontal_angle=None, clutch_angle=None, interrupt=False):
        if not self.is_running:
            raise AssertionError("tried to shutdown not running Eezybot")
        else:
            self.is_running = False
            self.base.shutdown(base_angle, interrupt=interrupt)
            self.verticalArm.shutdown(vertical_angle, interrupt=interrupt)
            self.horizontalArm.shutdown(horizontal_angle, interrupt=interrupt)
            self.clutch.shutdown(clutch_angle, interrupt=interrupt)
            _pool.close()

        return self

    def start(self):
        if self.is_running:
            raise AssertionError("tried to start still running Eezybot")
        else:
            global _pool
            _pool = multiprocessing.pool.ThreadPool(4)
            self.base.start()
            self.verticalArm.start()
            self.horizontalArm.start()
            self.clutch.start()
            self.is_running = True
        return self

    def print_performed_rotations(self, bool):
        self.base.print_performed_rotations(bool)
        self.verticalArm.print_performed_rotations(bool)
        self.horizontalArm.print_performed_rotations(bool)
        self.clutch.print_performed_rotations(bool)
        return self

    def activate_key_listener(self):
        if self.__key_listener_activated:
            raise AssertionError("Key Listeners are already activated")
        elif not self.is_running:
            raise AssertionError("Eezybot has not been started yet, can't activate Key Listener")
        else:
            threading.Thread(target=self.__key_listener, daemon=True).start()
        return self

    def __key_listener(self):
        while self.is_running:
            key = sys.stdin.read(1)

            if str(key) == chr(27):
                print("shutting down Eezybot")
                self.to_default_and_shutdown()
                sys.exit(0)
            if str(key) == 'k':
                print("System Exit")
                sys.exit(0)
            if str(key) == 'c':
                print("clearing queue")
                self.clear_all_queues()
            if str(key) == 'r':
                print("to_default")
                self.to_default()

            if str(key) == 'q':
                self.base.rotate(self.base.wait().get_rotation() + cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'a':
                self.base.rotate(self.base.wait().get_rotation() - cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'w':
                self.verticalArm.rotate(self.verticalArm.wait().get_rotation() + cons.MANUEL_CONTROL.STEP)
            elif str(key) == 's':
                self.verticalArm.rotate(self.verticalArm.wait().get_rotation() - cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'e':
                self.horizontalArm.rotate(self.horizontalArm.wait().get_rotation() + cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'd':
                self.horizontalArm.rotate(self.horizontalArm.wait().get_rotation() - cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'r':
                self.clutch.rotate(self.clutch.wait().get_rotation() + cons.MANUEL_CONTROL.STEP)
            elif str(key) == 'f':
                self.clutch.rotate(self.clutch.wait().get_rotation() - cons.MANUEL_CONTROL.STEP)
            time.sleep(0.1)


eezybot = _Eezybot()
