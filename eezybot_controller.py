import sys
import threading
import time

from servo_controller import ServoController, Servo
import constants as cons


class _Base(Servo):

    def __init__(self):
        super().__init__(cons.BASE.CHANNEL, cons.BASE.MIN, cons.BASE.DEFAULT, cons.BASE.MAX)


class _ArmVertical(Servo):

    def __init__(self):
        super().__init__(cons.VERTICAL.CHANNEL, cons.VERTICAL.MIN, cons.VERTICAL.DEFAULT, cons.VERTICAL.MAX)


class _ArmHorizontal(Servo):

    def __init__(self):
        super().__init__(cons.HORIZONTAL.CHANNEL, cons.HORIZONTAL.MIN, cons.HORIZONTAL.DEFAULT, cons.HORIZONTAL.MAX)


class _Clutch(Servo):

    def __init__(self):
        super().__init__(cons.CLUTCH.CHANNEL, cons.CLUTCH.MIN, cons.CLUTCH.DEFAULT, cons.CLUTCH.MAX)

    def grab(self):
        return self.rotate(cons.CLUTCH.GRAB)

    def release(self):
        return self.rotate(cons.CLUTCH.RELEASE)


class _EezybotServoController(ServoController):

    def __init__(self):
        self.base = _Base()
        self.verticalArm = _ArmVertical()
        self.horizontalArm = _ArmHorizontal()
        self.clutch = _Clutch()
        super().__init__(self.base, self.verticalArm, self.horizontalArm, self.clutch)
        self.__key_listener_activated = False

    # ensures the last rotation of every Servo is to it's default angle.
    # if interrupt is True, it won't wait for all queued rotations to be performed and
    # instead cancels all currently performed rotations and clears the queues
    def to_default_and_shutdown(self, interrupt=False):
        return self.finish_and_shutdown(cons.BASE.DEFAULT, cons.VERTICAL.DEFAULT,
                                        cons.HORIZONTAL.DEFAULT,
                                        cons.CLUTCH.DEFAULT, interrupt=interrupt)

    # Eezybot must be started to activate Key Listeners
    # Key Listener is stopping when Eezybot shuts down
    def activate_key_listener(self):
        if self.__key_listener_activated:
            raise AssertionError("Key Listeners are already activated")
        else:
            self.__key_listener_activated = True
            threading.Thread(target=self.__key_listener, daemon=True).start()
        return self

    # Eezybot must be started to activate Key Listeners
    # Stops when Eezybot shuts down
    def __key_listener(self):
        def bounds_check(angle, min, max):
            if angle < min:
                return min
            elif angle > max:
                return max
            return angle

        step_size = cons.MANUEL_CONTROL.STEP
        while self.is_running():
            key = sys.stdin.read(1)

            if str(key) == chr(27):
                print("shutting down Eezybot")
                self.to_default_and_shutdown(interrupt=True)
                sys.exit(0)
            if str(key) == 'c':
                self.clear_all_queues()
                print("clearing queue")
            if str(key) == 'b':
                self.to_default()
                print("to_default")

            if str(key) == '+' or str(key) == 'm':
                step_size += 1
                print("Stepsize = {}".format(step_size))
            if str(key) == '+' or str(key) == 'n':
                step_size -= 1
                print("Stepsize = {}".format(step_size))

            if str(key) == 'q':
                angle = self.base.wait().get_rotation() + step_size
                self.base.rotate(bounds_check(angle, cons.BASE.MIN, cons.BASE.MAX))
            elif str(key) == 'a':
                angle = self.base.wait().get_rotation() - step_size
                self.base.rotate(bounds_check(angle, cons.BASE.MIN, cons.BASE.MAX))
            elif str(key) == 'e':
                angle = self.verticalArm.wait().get_rotation() + step_size
                self.verticalArm.rotate(bounds_check(angle, cons.VERTICAL.MIN, cons.VERTICAL.MAX))
            elif str(key) == 'd':
                angle = self.verticalArm.wait().get_rotation() - step_size
                self.verticalArm.rotate(bounds_check(angle, cons.VERTICAL.MIN, cons.VERTICAL.MAX))
            elif str(key) == 'w':
                angle = self.horizontalArm.wait().get_rotation() + step_size
                self.horizontalArm.rotate(bounds_check(angle, cons.HORIZONTAL.MIN, cons.HORIZONTAL.MAX))
            elif str(key) == 's':
                angle = self.horizontalArm.wait().get_rotation() - step_size
                self.horizontalArm.rotate(bounds_check(angle, cons.HORIZONTAL.MIN, cons.HORIZONTAL.MAX))
            elif str(key) == 'r':
                angle = self.clutch.wait().get_rotation() + step_size
                self.clutch.rotate(bounds_check(angle, cons.CLUTCH.MIN, cons.CLUTCH.MAX))
            elif str(key) == 'f':
                angle = self.clutch.wait().get_rotation() - step_size
                self.clutch.rotate(bounds_check(angle, cons.CLUTCH.MIN, cons.CLUTCH.MAX))
            time.sleep(0.1)
        self.__key_listener_activated = False


eezybot = _EezybotServoController()
