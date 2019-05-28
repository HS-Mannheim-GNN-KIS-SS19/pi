import constants as cons
from key_listener import KeyListener
from servo_controller import ServoController, Servo, ServoKeyListener

if cons.MANUEL_CONTROL.RESOLVE_REWARDS:
    import reward_calculation


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


class _EezybotKeyListener(ServoKeyListener):
    if cons.MANUEL_CONTROL.RESOLVE_REWARDS:
        def print_rewards(self):
            old_state = self.state
            self.state = reward_calculation.get_current_state()
            print(reward_calculation.resolve_rewards(old_state, self.state))

        def step_up(self, servo):
            super().step_up(servo)
            self.print_rewards()

        def step_down(self, servo):
            super().step_down(servo)
            self.print_rewards()

    def __init__(self, *servo_tuples, step_control=("o", "p"), func_dictionary={}, until=True,
                 until_func=KeyListener.true_func):
        """

            calls given function when corresponding key is entered on console

            Note: Using the same key in a servo_tuple, step_control and the func_dictionary is not possible.
            This will result in the entries being overwritten func_dictionary < step_control < servo_tuple !!!

        :param servo_tuples: Tuple containing a servo on position 0 and two key for stepping up and down
                            (servo, "key1", "key2"),(servo,"key3", "key4")
        :param step_control: Tuple containing 2 key for increasing and decreasing step size
        :param func_dictionary: a python dictionary containing Tuples with a function and args as values
                    {"key":(func, arg1, arg2...),
                    "key2":(func2, arg1, arg2...)}
        :param until: boolean flag stopping the  key checking Thread if True
        :param until_func: function returning a boolean, stopping the  key checking Thread if True
        """
        if cons.MANUEL_CONTROL.RESOLVE_REWARDS:
            self.state = reward_calculation.get_current_state()
        super().__init__(*servo_tuples, step_control=step_control, func_dictionary=func_dictionary, until=until,
                         until_func=until_func)


class _EezybotServoController(ServoController):

    def __init__(self):
        self.base = _Base()
        self.verticalArm = _ArmVertical()
        self.horizontalArm = _ArmHorizontal()
        self.clutch = _Clutch()
        super().__init__(self.base, self.verticalArm, self.horizontalArm, self.clutch)
        self.__key_listener_activated = False

    def to_default_and_shutdown(self, interrupt=False):
        """
        ensures the last rotation of every Servo is to it's default angle.
        if interrupt is True, it won't wait for all queued rotations to be performed and
        instead cancels all currently performed rotations and clears the queues
        """
        return self.finish_and_shutdown(cons.BASE.DEFAULT, cons.VERTICAL.DEFAULT,
                                        cons.HORIZONTAL.DEFAULT,
                                        cons.CLUTCH.DEFAULT, interrupt=interrupt)

    def finish_and_shutdown(self, base_angle=None, arm_vertical_angle=None, arm_horizontal_angle=None,
                            clutch_angle=None, interrupt=False):
        return super().finish_and_shutdown(base_angle, arm_vertical_angle, arm_horizontal_angle, clutch_angle,
                                           interrupt=interrupt)

    def activate_key_listener(self):
        """
        Eezybot must be started to activate Key Listeners
        Key Listener is stopping when Eezybot shuts down

        """

        def shutdown():
            self.to_default_and_shutdown(interrupt=True).wait_for_shutdown()
            print("shut down Eezybot")

        def clear():
            self.clear_all_queues()
            print("clearing queue")

        def to_default():
            self.to_default()
            print("to_default")

        _EezybotKeyListener((self.base, "q", "a"), (self.verticalArm, "e", "d"), (self.horizontalArm, "w", "s"),
                            (self.clutch, "r", "f"), step_control=("t", "g"),
                            func_dictionary={"k": (shutdown,), "c": (clear,), "v": (to_default,)},
                            until_func=self.is_running)
        return self


eezybot = _EezybotServoController()
