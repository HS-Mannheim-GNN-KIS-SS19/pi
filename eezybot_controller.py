from constants import EEZYBOT_CONTROLLER as EEZYBOT
from image_processing_interface import get_state
from key_listener import KeyListener
from servo_controller import ServoController, Servo, ServoKeyListener

if EEZYBOT.MANUEL_CONTROL.RESOLVE_REWARDS:
    import reward_calculation


class _Base(Servo):

    def __init__(self):
        super().__init__(EEZYBOT.BASE.CHANNEL, EEZYBOT.BASE.MIN, EEZYBOT.BASE.MAX,
                         default_angle=EEZYBOT.BASE.DEFAULT, name="Base",
                         step_size=EEZYBOT.BASE.STEP_SIZE, step_time=EEZYBOT.BASE.STEP_TIME)


class _ArmVertical(Servo):

    def __init__(self):
        super().__init__(EEZYBOT.VERTICAL.CHANNEL, EEZYBOT.VERTICAL.MIN, EEZYBOT.VERTICAL.MAX,
                         default_angle=EEZYBOT.VERTICAL.DEFAULT, name="Vertical Arm",
                         step_size=EEZYBOT.VERTICAL.STEP_SIZE, step_time=EEZYBOT.VERTICAL.STEP_TIME)


class _ArmHorizontal(Servo):

    def __init__(self):
        super().__init__(EEZYBOT.HORIZONTAL.CHANNEL, EEZYBOT.HORIZONTAL.MIN, EEZYBOT.HORIZONTAL.MAX,
                         default_angle=EEZYBOT.HORIZONTAL.DEFAULT, name="Horizontal Arm",
                         step_size=EEZYBOT.HORIZONTAL.STEP_SIZE, step_time=EEZYBOT.HORIZONTAL.STEP_TIME)


class _Clutch(Servo):

    def __init__(self):
        super().__init__(EEZYBOT.CLUTCH.CHANNEL, EEZYBOT.CLUTCH.MIN, EEZYBOT.CLUTCH.MAX,
                         default_angle=EEZYBOT.CLUTCH.DEFAULT, name="Clutch",
                         step_size=EEZYBOT.CLUTCH.STEP_SIZE, step_time=EEZYBOT.HORIZONTAL.STEP_TIME)

    def grab(self):
        return self.rotate_to(EEZYBOT.CLUTCH.GRAB)

    def release(self):
        return self.rotate_to(EEZYBOT.CLUTCH.RELEASE)


class _EezybotKeyListener(ServoKeyListener):
    if EEZYBOT.MANUEL_CONTROL.RESOLVE_REWARDS:
        def print_rewards(self):
            old_state = self.state
            self.state = get_state()
            print("State: {}".format(self.state))
            print("Rewards: {}".format(reward_calculation.resolve_rewards(old_state, self.state, True)))

        def step_up(self, servo):
            super().step_up(servo)
            self.print_rewards()

        def step_down(self, servo):
            super().step_down(servo)
            self.print_rewards()

    def __init__(self, *servo_tuples, step_control=("o", "p"), func_dictionary=None,
                 while_func=KeyListener.always_true):
        """

            calls given function when corresponding key is entered on console

            may print Rewards after each step if MANUEL_CONTROL.RESOLVE_REWARDS in constants.py is True

            Note: Using the same key in a servo_tuple, step_control and the func_dictionary is not possible.
            This will result in the entries being overwritten func_dictionary < step_control < servo_tuple !!!

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

        if EEZYBOT.MANUEL_CONTROL.RESOLVE_REWARDS:
            self.state = get_state()
        super().__init__(*servo_tuples, step_control=step_control, func_dictionary=func_dictionary,
                         while_func=while_func)


class _EezybotServoController(ServoController):

    def __init__(self):
        self.base = _Base()
        self.verticalArm = _ArmVertical()
        self.horizontalArm = _ArmHorizontal()
        self.clutch = _Clutch()
        super().__init__(self.base, self.verticalArm, self.horizontalArm, self.clutch)
        self.__key_listener_activated = False

    def to_default_and_shutdown(self, dump_rotations=False):
        """
            ensures the last rotation of every Servo is to it's default angle.
            if dump_rotations is True, it won't wait for all queued rotations to be performed and
            instead cancels all currently performed rotations and clears the queues
        """
        return self.finish_and_shutdown(EEZYBOT.BASE.DEFAULT, EEZYBOT.VERTICAL.DEFAULT,
                                        EEZYBOT.HORIZONTAL.DEFAULT,
                                        EEZYBOT.CLUTCH.DEFAULT, dump_rotations=dump_rotations)

    def finish_and_shutdown(self, base_angle=None, arm_vertical_angle=None, arm_horizontal_angle=None,
                            clutch_angle=None, dump_rotations=False):
        return super().finish_and_shutdown(base_angle, arm_vertical_angle, arm_horizontal_angle, clutch_angle,
                                           dump_rotations=dump_rotations)

    def activate_key_listener(self):
        """
            Eezybot must be started to activate Key Listeners
            Key Listener is stopping when Eezybot shuts down
        """

        def shutdown():
            self.to_default_and_shutdown(dump_rotations=True).join()
            print("shut down Eezybot")

        def clear():
            self.dump_rotations()
            print("dump all rotations")

        def to_default():
            self.to_default()
            print("to_default")

        _EezybotKeyListener((self.base, "q", "a"), (self.verticalArm, "e", "d"), (self.horizontalArm, "w", "s"),
                            (self.clutch, "r", "f"), step_control=("t", "g"),
                            func_dictionary={"k": (shutdown,), "c": (clear,), "b": (to_default,)},
                            while_func=self.is_running)
        return self


eezybot = _EezybotServoController()
