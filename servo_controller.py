"""Base Class Provider"""

import sys
import threading
import time
from typing import Tuple

from constants import SERVO_CONTROLLER as SERVO
from key_listener import KeyListener

if not SERVO.USE_FAKE_CONTROLLER:
    import adafruit_servokit
else:
    # Dummy Class for Testing
    # noinspection PyPep8Naming
    class adafruit_servokit:
        class ServoValue:
            def __init__(self):
                self.angle = 0

        servo = [ServoValue(), ServoValue(), ServoValue(), ServoValue()]

        # noinspection PyUnusedLocal
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

    def __init__(self, channel_number, min_degree, default_degree, max_degree, name=None):

        # IGNORE ERROR: imports depending on Python version
        is_pi2 = sys.version_info < (3, 0)
        if is_pi2:
            # noinspection PyUnresolvedReferences
            from Queue import Queue
        else:
            # noinspection PyUnresolvedReferences
            from queue import Queue

        # Bounds
        self.min_degree = min_degree
        self.default_degree = default_degree
        self.max_degree = max_degree

        # Components
        self.__channel_number = channel_number
        if name is None:
            self.name = "Servo {}".format(channel_number)
        else:
            self.name = name
        self.__rotation_controller_thread = None
        # https://docs.python.org/2/library/queue.html
        self.__rotation_queue = Queue()
        self.__wait_for_other_servo_queue = Queue()

        # Flags
        self.__print_rotations = False
        self.__dump_rotations = False
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    """-----------------------------START & SHUT DOWN----------------------------------------------------"""

    def start(self):
        """
            Creating Thread running the Rotation Control Function which takes Rotations from queue and performs them

        :raises AlreadyStartedException
        """
        if self.__rotation_controller_thread is not None and self.__rotation_controller_thread.is_alive():
            raise AlreadyStartedException("{} is already started".format(self.name))
        else:
            self.__rotation_controller_thread = threading.Thread(target=self.__rotation_control, daemon=True)
            self.__rotation_controller_thread.start()
        return self

    def shutdown(self):
        """
            sets flag to shutdown the Rotation Control Thread
            Is not waiting for all rotations to be performed
        """
        self.__shutdown_rotation_controller = True
        return self

    def _finish_and_shutdown(self, final_rotation=None, dump_rotations=False):
        """
          sets flag to prevent new rotations to be added to the queue
          then waits for all rotations to be performed
          finally sets flag to shutdown the Rotation Control Thread

      :param final_rotation: the last rotation before shutting down will be of this angle
      :param dump_rotations: if True, currently performed rotation as well as all queued rotations will be canceled.

      :raises NotStartedException
      """
        if self.__rotation_controller_thread is None or not self.__rotation_controller_thread.is_alive():
            raise NotStartedException(
                "{} wasn't running but tried to shut down".format(self.name))
        else:
            self.__block_rotate_method = True
            if dump_rotations:
                self.dump_rotations()
            self.wait()
            if final_rotation is not None:
                self.__rotation_queue.put(final_rotation)
            self.wait()
            self.__shutdown_rotation_controller = True
        return self

    def finish_and_shutdown(self, final_rotation=None, dump_rotations=False):
        threading.Thread(target=self._finish_and_shutdown,
                         kwargs={"dump_rotations": dump_rotations,
                                 "final_rotation": final_rotation},
                         daemon=True).start()
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
                    self.name, angle))
        elif angle < self.min_degree:
            raise AngleTooLittleException(
                "{} Rotation out of Bounds: cur: {} < min: {}".format(self.name, angle,
                                                                      self.min_degree))
        elif angle > self.max_degree:
            raise AngleTooBigException(
                "{} Rotation out of Bounds: cur: {} > max: {}".format(self.name, angle,
                                                                      self.max_degree))
        else:
            self.__rotation_queue.put(angle)
        return self

    def resolve_degree_from_relative(self, value):
        """
            resolves degree from relative value

        :param value: 1 >= value >= 0
        """
        return self.min_degree + int(value * (self.max_degree - self.min_degree))

    def rotate_relative(self, value):
        """
            resolves absolute angle from given relative value then calls rotate with resolved angle

        :param value: 1 >= value >= 0
        """
        self.rotate(self.resolve_degree_from_relative(value))
        return self

    def to_default(self):
        self.rotate(self.default_degree)
        return self

    def step(self, value):
        """
            changes rotation by the given value

        :param value: offset to be applied to the current angle
        """
        self.rotate(ensure_in_bounds(self.get_rotation()) + value)
        return self

    """-----------------------------WAIT----------------------------------------------------"""

    def join(self, timeout=None):
        """
            blocks until the Rotation Control Thread of this Servo is not alive

        :param timeout: if timeout is not None, this function will stop blocking if the timeout is reached.
                        Note: No Exception is thrown, check for timeouts through is_running() function
        """
        if self.__rotation_controller_thread is not None:
            self.__rotation_controller_thread.join(timeout)
        return self

    def wait(self):
        """
            calling Thread waits until the rotation queue of this Servo is empty
        """
        self.__rotation_queue.join()
        return self

    def wait_for_servo(self, *servos):
        """
            makes this Servo wait for other Servos emptying their queue

        :param servos: servos to be waited for
        """
        for servo in servos:
            self.__wait_for_other_servo_queue.put(servo)
        return self

    """-----------------------------ROTATION EXECUTION----------------------------------------------------"""

    def __rotation_control(self):
        """
            runs permanently checking for new rotation requests. Runs in a new Thread after calling start() Function

        :flag self.__shutdown_rotation_controller: breaks the loop, ending the Thread
        :flag self.__dump_rotations: Empty the queue
        :flag not self.__wait_for_other_servo_queue.empty(): waits on every Servo in the queue
        """
        from queue import Empty
        while not self.__shutdown_rotation_controller:
            while not self.__wait_for_other_servo_queue.empty():
                self.__wait_for_other_servo_queue.get().wait()
            if self.__dump_rotations:
                while not self.__rotation_queue.empty():
                    self.__rotation_queue.get_nowait()
                    self.__rotation_queue.task_done()
                self.__dump_rotations = False
            try:
                # blocking if queue is empty
                angle = self.__rotation_queue.get(timeout=0.1)
                while not self.__wait_for_other_servo_queue.empty():
                    self.__wait_for_other_servo_queue.get().wait()
                self.__run_rotation(angle)
                self.__rotation_queue.task_done()
            except Empty:
                # raised on timeout
                # what a brilliant Exception Name...
                pass
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    def __run_rotation(self, angle):
        """
            performs actual rotation to a given angle
            
        :flag self.__dump_rotations: cancel performed rotation
        """

        def perform_rotation_step_to(degree):
            _kit.servo[self.__channel_number].angle = degree
            time.sleep(SERVO.STEP.TIME)

        cur_angle = ensure_in_bounds(_kit.servo[self.__channel_number].angle)
        delta = angle - cur_angle

        # divide delta in steps which will be added on the current angle until the destined angle is reached
        for _ in range(int(abs(delta) / SERVO.STEP.SIZE)):
            if delta < 0:
                cur_angle -= SERVO.STEP.SIZE
            else:
                cur_angle += SERVO.STEP.SIZE
            if self.__dump_rotations:
                return
            perform_rotation_step_to(cur_angle)
        if self.__dump_rotations:
            return
        if delta % SERVO.STEP.SIZE != 0:
            perform_rotation_step_to(cur_angle)
        if self.__print_rotations:
            print("servo {} performed movement to: {}".format(self.name,
                                                              _kit.servo[self.__channel_number].angle))

    """-----------------------------MISC----------------------------------------------------"""

    def dump_rotations(self):
        """
            stop current rotation and clear all rotations from the queue
        """
        self.__dump_rotations = True
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
        # noinspection PyTypeChecker
        self.servos = servos  # type: Tuple[Servo]

    def start(self):
        """
            starts the Thread of every servo which is performing queued rotations
        """
        for servo in self.servos:
            if not servo.is_running():
                servo.start()
        return self

    def interrupt(self):
        """
            sets flag to shutdown the Rotation Control Threads of every Servo in the servo list
            Is not waiting for all rotations to be performed
        """
        for servo in self.servos:
            servo.shutdown()
        return self

    def finish_and_shutdown(self, *args, dump_rotations=False):
        """
            ensures the last rotation of the Servo with the same index in the servo list as in the args position
            is the angle given at the corresponding position in args.
            if you do not want to change the angle of servos but servos and index positions behind these,
            args at the index of those you do not wanna change should be None
            if dump_rotations is True, it won't wait for all queued rotations to be performed and
            instead cancels all currently performed rotations and clears the queues
        """
        for i, servo in enumerate(self.servos):
            servo.finish_and_shutdown(dump_rotations=dump_rotations, final_rotation=args[i] if i < len(args) else None)
        return self

    def join(self, timeout=None):
        """
            blocks until the Rotation Control Thread of every Servo was not alive once

        :param timeout: if timeout is not None, this function will stop blocking on timeout.
                        Note: No Exception is thrown, check for timeouts through is_running() function
        """
        if timeout is None:
            for servo in self.servos:
                servo.join()
        else:
            start_time = time.time()
            for servo in self.servos:
                remaining_time = timeout - (time.time() - start_time)
                servo.join(remaining_time)
        return self

    def dump_rotations(self):
        """
            interrupts all rotations and clears the queue of every Servo
        """
        for servo in self.servos:
            servo.dump_rotations()
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
    def bounds_check(angle, min_degree, max_degree):
        if angle < min_degree:
            return min_degree
        elif angle > max_degree:
            return max_degree
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

    def __init__(self, *servo_tuples, step_control=("o", "p"), func_dictionary=None,
                 while_func=KeyListener.always_true):
        """

            calls given function when corresponding key is entered on console

            Note: Using the same key in a servo_tuple, step_control and the func_dictionary is not possible.
            This will result in entries being overwritten func_dictionary < step_control < servo_tuple !!!

        :param servo_tuples:    Tuple containing a servo and two keys for stepping up and down
                                Bsp:    (servo,"key1", "key2"), (servo,"key3", "key4")
        :param step_control:    Tuple containing 2 keys for increasing and decreasing step size
        :param func_dictionary: a python dictionary containing Tuples with a function and 0 or more args
                                Bsp:    {"key":(func, arg1, arg2...),
                                        "key2":(func2, arg1, arg2...)}
        :param while_func:      function returning a boolean. Stops the key checking Thread if False
                                default function returns always True
        """

        # because a mutable should not be a default value
        if func_dictionary is None:
            func_dictionary = {}

        self.step_size = SERVO.MANUEL_CONTROL.DEFAULT_STEP_SIZE
        func_dictionary.update({step_control[0]: (self.step_size_up,), step_control[1]: (self.step_size_down,)})
        for servo_tuple in servo_tuples:
            func_dictionary.update(
                {servo_tuple[1]: (self.step_up, servo_tuple[0]), servo_tuple[2]: (self.step_down, servo_tuple[0])})
        super().__init__(func_dictionary, while_func)
