"""Base Class Provider"""

import sys
import threading
import time
from typing import Tuple
from constants import STEP, USE_FAKE_CONTROLLER, MANUEL_CONTROL
from key_listener import KeyListener

if not USE_FAKE_CONTROLLER:
    import adafruit_servokit
else:
    # Dummy Class for Testing
    class adafruit_servokit:
        class ServoValue:
            def __init__(self):
                self.angle = 0

        servo = [ServoValue(), ServoValue(), ServoValue(), ServoValue()]

        @staticmethod
        def ServoKit(channels=8):
            return adafruit_servokit

"""
Set channels to the number of servo channels on your kit.
8 for FeatherWing, 16 for Shield/HAT/Bonnet.
"""
_kit = adafruit_servokit.ServoKit(channels=8)


class OutOfBoundsException(Exception):
    pass


class AngleTooLittleException(OutOfBoundsException):
    pass


class AngleTooBigException(OutOfBoundsException):
    pass


class NotStartedException(Exception):
    pass


class ShutDownException(Exception):
    pass


class AlreadyStartedException(Exception):
    pass


def ensure_in_bounds(angle):
    """
    Ensures the Servos current rotation is in Bounds (min: 0, max: 180)
    """
    if angle < 0:
        return 0
    elif angle > 180:
        return 180
    else:
        return angle


class Servo:

    def __init__(self, channel_number, min_degree, default_degree, max_degree):

        # IGNORE ERROR: imports depending on Python version
        IS_PI2 = sys.version_info < (3, 0)
        if IS_PI2:
            from Queue import Queue
        else:
            from queue import Queue

        # Bounds
        self.min_degree = min_degree
        self.default_degree = default_degree
        self.max_degree = max_degree

        # Components
        self.__channel_number = channel_number
        self.__rotation_controller_thread = None
        # https://docs.python.org/2/library/queue.html
        self.__queue = Queue()
        self.__wait_for_other_servos_queue = Queue()

        # Flags
        self.__print_rotations = False
        self.__clear_queue = False
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    """-----------------------------START & SHUT DOWN----------------------------------------------------"""

    def start(self):
        """
        Creating Thread running the Rotation Control Function which takes Rotations from queue and performs them

        :raises AlreadyStartedException
        """
        if self.__rotation_controller_thread is not None and self.__rotation_controller_thread.is_alive():
            raise AlreadyStartedException("Servo {) is already started".format(self.__class__.__name__[1:]))
        else:
            self.__rotation_controller_thread = threading.Thread(target=self.__rotation_control, daemon=True)
            self.__rotation_controller_thread.start()
        return self

    def shutdown(self, final_rotation=None, interrupt=False):
        """
        sets flag to prevent new rotations to be added to queue
        then waits for the queue to be empty
        finally sets flag to shutdown the Rotation Control Thread

        :param final_rotation: if an value is given to final_rotation the last rotation before shutting down will be of this angle
        :param interrupt: if interrupt is True currently performed rotation as well as all queued rotations will be canceled.

        :raises NotStartedException
        """
        if self.__rotation_controller_thread is None or not self.__rotation_controller_thread.is_alive():
            raise NotStartedException(
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
        return self

    """-----------------------------ADD ROTATION TO QUEUE----------------------------------------------------"""

    def rotate(self, angle):
        """
        adds the given angle to the queue of rotations to be performed by the rotation controller thread.

        :raises ShutDownException: if shutdown is currently performed
        :raises AngleTooLittleException
        :raises AngleTooBigException
        """
        if self.__block_rotate_method:
            raise ShutDownException(
                "{} can not perform rotation to {}: Servo Controller is shutting down".format(
                    self.__class__.__name__[1:], angle))
        elif angle < self.min_degree:
            raise AngleTooLittleException(
                "{} Rotation out of Bounds: cur: {} < min: {}".format(self.__class__.__name__[1:], angle,
                                                                      self.min_degree))
        elif angle > self.max_degree:
            raise AngleTooBigException(
                "{} Rotation out of Bounds: cur: {} > max: {}".format(self.__class__.__name__[1:], angle,
                                                                      self.max_degree))
        else:
            self.__queue.put(angle)
        return self

    def resolve_degree_from_relative(self, value):
        """
        resolves degree from relative value
        """
        return self.min_degree + int(value * (self.max_degree - self.min_degree))

    def rotate_relative(self, value):
        """
        resolves absolute angle from given relative value then calls rotate with resolved angle
        """
        self.rotate(self.resolve_degree_from_relative(value))
        return self

    def to_default(self):
        self.rotate(self.default_degree)
        return self

    def step(self, value):
        self.rotate(ensure_in_bounds(self.get_rotation()) + value)
        return self

    """-----------------------------WAIT----------------------------------------------------"""

    def join(self, timout=None):
        if self.__rotation_controller_thread is not None:
            self.__rotation_controller_thread.join(timout)
        return self

    def wait(self):
        """
        Calling Thread waits until the rotation queue of this Servo is empty
        """
        self.__queue.join()
        return self

    def wait_for_servo(self, *servos):
        """
        makes this Servo wait for another Servo emptying it's queue
        :param servos: servos to be waited for
        """
        for servo in servos:
            self.__wait_for_other_servos_queue.put(servo)
        return self

    """-----------------------------ROTATION EXECUTION----------------------------------------------------"""

    def __rotation_control(self):
        """
        runs permanently checking for new rotation requests. Runs in new Thread after calling start() Function
        """
        from queue import Empty
        while not self.__shutdown_rotation_controller:
            while not self.__wait_for_other_servos_queue.empty():
                self.__wait_for_other_servos_queue.get().wait()
            if self.__clear_queue:
                while not self.__queue.empty():
                    self.__queue.get_nowait()
                    self.__queue.task_done()
                self.__clear_queue = False
            try:
                # blocking if queue is empty
                angle = self.__queue.get(timeout=0.1)
                self.__run_rotation(angle)
                self.__queue.task_done()
            except Empty:
                pass
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    def __run_rotation(self, angle):
        """
         performs actual rotation to a given angle
        """
        cur_angle = ensure_in_bounds(_kit.servo[self.__channel_number].angle)
        delta = angle - cur_angle

        # divide delta in steps which will be added on the current angle until the destined angle is reached
        for _ in range(int(abs(delta) / STEP.SIZE)):
            if delta < 0:
                cur_angle -= STEP.SIZE
            else:
                cur_angle += STEP.SIZE
            if self.__clear_queue:
                return
            self.__step_to(cur_angle)
        if self.__clear_queue:
            return
        if delta % STEP.SIZE != 0:
            self.__step_to(cur_angle)
        if self.__print_rotations:
            print("servo {} performed movement to: {}".format(self.__class__.__name__[1:],
                                                              _kit.servo[self.__channel_number].angle))

    def __step_to(self, angle):
        _kit.servo[self.__channel_number].angle = angle
        time.sleep(STEP.TIME)

    """-----------------------------MISC----------------------------------------------------"""

    def clear_queue(self):
        """
        stops and clears all rotations
        """
        self.__clear_queue = True
        return self

    def get_rotation(self):
        return _kit.servo[self.__channel_number].angle

    def print_performed_rotations(self, bol):
        self.__print_rotations = bol
        return self

    def is_running(self):
        if self.__rotation_controller_thread is not None:
            return self.__rotation_controller_thread.is_alive()
        else:
            return False


class ServoController:

    def __init__(self, *servos):
        self.servos = servos  # type: Tuple[Servo]

    def start(self):
        """
        starts the Thread of every servo which is performing queued rotations
        """
        for servo in self.servos:
            if not servo.is_running():
                servo.start()
        return self

    def finish_and_shutdown(self, *args, interrupt=False):
        """
        ensures the last rotation of the Servo in the servo list with the same index as the args position is the angle given in args
        if you don t want to change the angle of servos but servos behind these,
        arg at the index for these should be None
        if interrupt is True, it won't wait for all queued rotations to be performed and
        instead cancels all currently performed rotations and clears the queues
        """
        for i, servo in enumerate(self.servos):
            threading.Thread(target=servo.shutdown, args=(args[i] if i < len(args) else None,),
                             kwargs={"interrupt": interrupt},
                             daemon=True).start()
        return self

    def wait_for_shutdown(self, timeout=None):
        for servo in self.servos:
            servo.join(timeout)
        return self

    def clear_all_queues(self):
        """
            interrupts and clears all queued rotations
        """
        for servo in self.servos:
            servo.clear_queue()
        return self

    def wait_for_all(self):
        """
        blocks until all queued movements are performed
        """
        for servo in self.servos:
            servo.wait()
        return self

    def to_default(self):
        for servo in self.servos:
            servo.to_default()
        return self

    def is_running(self):
        return all([servo.is_running() for servo in self.servos])

    def print_performed_rotations(self, bol):
        for servo in self.servos:
            servo.print_performed_rotations(bol)
        return self


class ServoKeyListener(KeyListener):
    @staticmethod
    def bounds_check(angle, min, max):
        if angle < min:
            return min
        elif angle > max:
            return max
        return angle

    def step_up(self, servo):
        angle = servo.wait().get_rotation() + self.step_size
        servo.rotate(self.bounds_check(angle, servo.min_degree, servo.max_degree))

    def step_down(self, servo):
        angle = servo.wait().get_rotation() - self.step_size
        servo.rotate(self.bounds_check(angle, servo.min_degree, servo.max_degree))

    def step_size_up(self):
        self.step_size += 1
        print("Step Size increased to {}".format(self.step_size))

    def step_size_down(self):
        self.step_size -= 1
        print("Step Size decreased to {}".format(self.step_size))

    def __init__(self, *servo_tuples, step_control=("o", "p"), func_dictionary={}, until=True,
                 until_func=KeyListener.true_func):
        """
            calls given function when corresponding key is entered on console

            Note: Using the same key in a servo_tuple and the funcDictionary is not possible.
            This will result in the entry in the funcDictionary disappearing !!!

        :param servo_tuples: Tuple containing a servo on position 0 and two key for stepping up and down
                            ("key1", "key2", servo),("key3", "key4", servo)
        :param step_control: Tuple containing 2 key for increasing and decreasing step size
        :param func_dictionary: a python dictionary containing Tuples with a function and args as values
                    {"key":(func, arg1, arg2...),
                    "key2":(func2, arg1, arg2...)}
        :param until: boolean flag stopping the  key checking Thread if True
        :param until_func: function returning a boolean, stopping the  key checking Thread if True
        """
        self.step_size = MANUEL_CONTROL.STEP

        func_dictionary.update({step_control[0]: (self.step_size_up,), step_control[1]: (self.step_size_down,)})
        for servo_tuple in servo_tuples:
            func_dictionary.update(
                {servo_tuple[1]: (self.step_up, servo_tuple[0]), servo_tuple[2]: (self.step_down, servo_tuple[0])})
        super().__init__(func_dictionary, until, until_func)
