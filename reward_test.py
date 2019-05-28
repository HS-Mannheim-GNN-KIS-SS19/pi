import time

import numpy as np

from constants import ENV, MANUEL_CONTROL
from eezybot_controller import eezybot
from image_processing_interface import get_state
from key_listener import KeyListener
from servo_controller import ServoKeyListener


def get_current_state() -> (float, float, float):
    state = get_state()
    return state if state is not None else (0, 0, 0)


def vector_length(vector):
    return np.math.sqrt(sum(i ** 2 for i in vector))


def distance_reward(old_state, new_state):
    return vector_length(new_state) - vector_length(old_state)


def radius_reward(old_r, new_r):
    return new_r - old_r


def resolve_rewards(old_state, new_state):
    if new_state == (0, 0, 0):
        return -10
    d_reward = distance_reward(old_state[0:2], new_state[0:2])
    r_reward = radius_reward(old_state[2], new_state[2])
    reward = d_reward * ENV.D_REWARD_MULTIPLIER + r_reward * ENV.R_REWARD_MULTIPLIER
    return "Reward: {}, Distance Reward: {}, Radius Reward: {}".format(reward, d_reward * ENV.D_REWARD_MULTIPLIER,
                                                                       r_reward * ENV.R_REWARD_MULTIPLIER)


class ActionServoKeyListener(KeyListener):
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

        self.state = get_current_state()

        def print_rewards():
            old_state = self.state
            state = get_current_state()
            print(resolve_rewards(old_state, state))

        def bounds_check(angle, min, max):
            if angle < min:
                return min
            elif angle > max:
                return max
            return angle

        self.step_size = MANUEL_CONTROL.STEP

        def step_size_up():
            self.step_size += 1
            print("Step Size increased to {}".format(self.step_size))

        def step_size_down():
            self.step_size -= 1
            print("Step Size decreased to {}".format(self.step_size))

        def step_up(servo):
            angle = servo.wait().get_rotation() + self.step_size
            servo.rotate(bounds_check(angle, servo.min_degree, servo.max_degree))
            print_rewards()

        def step_down(servo):
            angle = servo.wait().get_rotation() - self.step_size
            servo.rotate(bounds_check(angle, servo.min_degree, servo.max_degree))
            print_rewards()

        for servo_tuple in servo_tuples:
            func_dictionary.update(
                {servo_tuple[1]: (step_up, servo_tuple[0]), servo_tuple[2]: (step_down, servo_tuple[0])})
        func_dictionary.update({step_control[0]: (step_size_up,), step_control[1]: (step_size_down,)})
        super().__init__(func_dictionary, until, until_func)


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

    ActionServoKeyListener((self.base, "q", "a"), (self.verticalArm, "e", "d"), (self.horizontalArm, "w", "s"),
                           (self.clutch, "r", "f"), step_control=("t", "g"),
                           func_dictionary={"k": (shutdown,), "c": (clear,), "v": (to_default,)},
                           until_func=self.is_running)
    return self


eezybot.start()
time.sleep(1)
eezybot.activate_key_listener()

