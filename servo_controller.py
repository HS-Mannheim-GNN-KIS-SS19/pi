"""Base Class Provider"""

import threading
import time
import sys
from typing import Tuple
from constants import STEP_CONTROL, USE_FAKE_CONTROLLER

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

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
_kit = adafruit_servokit.ServoKit(channels=8)


class Servo:

    def __init__(self, channel_number, min_degree, default_degree, max_degree):

        # IGNORE ERROR
        # imports depending on Python version
        _IS_PI2 = sys.version_info < (3, 0)
        if _IS_PI2:
            from Queue import Queue
        else:
            from queue import Queue

        # Bonds
        self.__min_degrees = min_degree
        self.__default_degree = default_degree
        self.__max_degrees = max_degree

        # Components
        self.__channel_number = channel_number
        self.__rotation_controller_thread = None
        # https://docs.python.org/2/library/queue.html
        self.__queue = Queue()

        # Flags
        self.__wait_for_other_servos_queue = Queue()
        self.__print_rotations = False
        self.__clear_queue = False
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    # Creating Thread running the Rotation Control Function witch takes Rotations from queue and performs them
    def start(self):
        if self.__rotation_controller_thread is not None and self.__rotation_controller_thread.is_alive():
            raise AssertionError("Servo {) is already started".format(self.__class__.__name__[1:]))
        else:
            self.__rotation_controller_thread = threading.Thread(target=self.__rotation_control, daemon=True)
            self.__rotation_controller_thread.start()
        return self

    # adds new Rotation to given angle to the queue.
    # Movement will be performed through the rotation controller calling the __run_rotation(angle) function
    # Raises AssertionError if self.__block_rotate_method Flag is True or given angle is out of bounds
    def rotate(self, angle):
        if self.__block_rotate_method:
            raise AssertionError("Can not perform rotation to {}: Servo Controller is shutting down".format(angle))
        else:
            if angle < self.__min_degrees:
                raise AssertionError("Rotation out of Bounds: cur: {} < min: {}".format(angle, self.__min_degrees))
            elif angle > self.__max_degrees:
                raise AssertionError("Rotation out of Bounds: cur: {} > max: {}".format(angle, self.__max_degrees))
            else:
                self.__queue.put(angle)
        return self

    # resolves degree from relative value
    def _resolveDegree(self, value):
        return self.__min_degrees + int(value * (self.__max_degrees - self.__min_degrees))

    # resolves absolute angle from given relative value then calls rotate with resolved angle
    def rotate_relative(self, value):
        self.rotate(self._resolveDegree(value))
        return self

    # runs permanently checking for new rotation requests. Runs in new Thread after calling start() Function
    def __rotation_control(self):
        from queue import Empty
        while not self.__shutdown_rotation_controller:
            while not self.__wait_for_other_servos_queue.empty():
                self.__wait_for_other_servos_queue.get().wait()
            if self.__clear_queue:
                self.__clear_queue = False
                while not self.__queue.empty():
                    self.__queue.get_nowait()
                    self.__queue.task_done()
            try:
                # block if queue is empty
                angle = self.__queue.get(timeout=0.1)
                self.__run_rotation(angle)
                self.__queue.task_done()
            except Empty:
                pass
        self.__block_rotate_method = False
        self.__shutdown_rotation_controller = False

    # Ensures the Servos current rotation is in Bounds (min: 0, max: 180).
    @staticmethod
    def _ensure_in_bounds(angle):
        if angle < 0:
            return 0
        elif angle > 180:
            return 180
        else:
            return angle

    # performs actual rotation to a given angle
    def __run_rotation(self, angle):
        cur_angle = self._ensure_in_bounds(_kit.servo[self.__channel_number].angle)
        # calculate delta betwe      en current angle and destined angle
        delta = angle - cur_angle

        # divide delta in steps witch will be added on the current angle until the destined angle is reached
        # Each time, moving and waiting are performed in an additional Thread.
        # It calculates the next angle in the meantime and then waits for the movement and waiting to be finished
        for _ in range(int(abs(delta) / STEP_CONTROL.SIZE)):
            if delta < 0:
                cur_angle -= STEP_CONTROL.SIZE
            else:
                cur_angle += STEP_CONTROL.SIZE
            if self.__clear_queue:
                return
            self.__step_to(cur_angle)
        if self.__clear_queue:
            return
        if delta % STEP_CONTROL.SIZE != 0:
            self.__step_to(cur_angle)
        if self.__print_rotations:
            print("servo {} performed movement to: {}".format(self.__class__.__name__[1:],
                                                              _kit.servo[self.__channel_number].angle))

    def __step_to(self, angle):
        _kit.servo[self.__channel_number].angle = angle
        time.sleep(STEP_CONTROL.TIME)

    # Calling Thread waits until the rotation queue of this Servo is empty
    def wait(self):
        self.__queue.join()
        return self

    # make this Servo wait for another Servo emptying it's queue
    def wait_for_servo(self, *servos):
        for servo in servos:
            self.__wait_for_other_servos_queue.put(servo)
        return self

    # stops and clears all rotations
    def clear_queue(self):
        self.__clear_queue = True
        return self

    # sets flag to prevent new rotations to be added to queue
    # then waits for the queue to be empty
    # finally sets flag to shutdown the Rotation Control Thread
    # if interrupt is true currently performed rotation as well as all queued rotations will be canceled.
    # if an value is given to final_rotation the last rotation before shutting down will be of this angle
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

    def get_rotation(self):
        return _kit.servo[self.__channel_number].angle

    def print_performed_rotations(self, bol):
        self.__print_rotations = bol
        return self

    def to_default(self):
        self.rotate(self.__default_degree)
        return self

    def join(self, timout=None):
        if self.__rotation_controller_thread is not None:
            self.__rotation_controller_thread.join(timout)
        return self

    def is_running(self):
        if self.__rotation_controller_thread is not None:
            return self.__rotation_controller_thread.is_alive()
        else:
            return False


class ServoController:

    def __init__(self, *servos):
        self.servos = servos  # type: Tuple[Servo]

    # interrupts and clears all queued rotations
    def clear_all_queues(self):
        for servo in self.servos:
            servo.clear_queue()
        return self

    # blocks until all queued movements are performed
    def wait_for_all(self):
        for servo in self.servos:
            servo.wait()
        return self

    def to_default(self):
        for servo in self.servos:
            servo.to_default()
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

    def is_running(self):
        return all([servo.is_running() for servo in self.servos])

    # starts the Thread of every queue witch is performing queued rotations
    def start(self):
        for servo in self.servos:
            if not servo.is_running():
                servo.start()
        return self

    def print_performed_rotations(self, bool):
        for servo in self.servos:
            servo.print_performed_rotations(bool)
        return self
