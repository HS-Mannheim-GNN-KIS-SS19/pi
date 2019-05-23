import cv2
import gym
import numpy as np
from gym import spaces

import raspi_camera
from constants import ENV
from eezybot_controller import eezybot
from image_processing_interface import *


def _take_picture():
    return raspi_camera.take_picture()


def _get_current_state() -> (float, float, float):
    return get_state()


def vectorLength(vector):
    return np.math.sqrt(sum(i ** 2 for i in vector))


def _distance_reward(old_state, new_state):
    return vectorLength(new_state) - vectorLength(old_state)


def _radius_reward(old_r, new_r):
    return new_r - old_r


def _map_action_to_action_tuple():
    actions = []
    for base_angle in range(ENV.SERVO_SPACE):
        for arm_vertical_angle in range(ENV.SERVO_SPACE):
            for arm_horizontal_angle in range(ENV.SERVO_SPACE):
                actions.append(((base_angle - ENV.STEP_SIZE) * 5, (arm_vertical_angle - ENV.STEP_SIZE) * 10,
                                (arm_horizontal_angle - ENV.STEP_SIZE) * 10))
    return actions


class EezybotEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        """The main OpenAI Gym class. It encapsulates an environment with
         arbitrary behind-the-scenes dynamics. An environment can be
         partially or fully observed.
         The main API methods that users of this class need to know are:
             step
             reset
             render
             close
             seed

         And set the following attributes:
             action_space: The Space object corresponding to valid actions
             observation_space: The Space object corresponding to valid observations
             reward_range: A tuple corresponding to the min and max possible rewards

         Note: a default reward range set to [-inf,+inf] already exists. Set it if you want a narrower range.

         The methods are accessed publicly as "step", "reset", etc.. The
         non-underscored versions are wrapper methods to which we may add
         functionality over time.
         """
        # image can only be None if we pipe through stdout
        self.image = None

        # Coordinate min/maxs
        # TODO: set to smallest/biggest distance from eezybot to marble
        self.min_distance_to_eezybot = 0
        self.max_distance_to_eezybot = float('inf')
        # Should be 27 actions: 3 servos ^ 3 actions
        self.action_space = spaces.Discrete(ENV.ACTION_SPACE)
        # A R^n space which describes all valid inputs our model knows (x, y, radius)
        self.observation_space = spaces.Box(-1.0, 1.0, shape=(3,),
                                            dtype=np.float32)

        self.reward_range = (-float('inf'), float('inf'))

        self.episode_over = False

        self.actions_tuple = _map_action_to_action_tuple()
        self.state = _get_current_state()
        if self.state is None:
            self.episode_over = True
        self.reset()

    def _resolve_reward(self, old_state, new_state):
        if(old_state is None or new_state is None):
            return -1
        d_reward = _distance_reward(old_state[0:2], new_state[0:2])
        r_reward = _radius_reward(old_state[2], old_state[2])
        return d_reward * r_reward

    # TODO
    def _is_episode_over(self, new_state):
        return self.episode_over

    def _take_action(self, action):
        base_angle, arm_vertical_angle, arm_horizontal_angle = self.actions_tuple[action]
        try:
            eezybot.base.step(base_angle)
        except Exception:
            print("Exception!!!")
        try:
            eezybot.verticalArm.step(arm_vertical_angle)
        except Exception:
            print("Exception!!!")
        try:
            eezybot.horizontalArm.step(arm_horizontal_angle)
        except Exception:
            print("Exception!!!")
        eezybot.start().finish_and_shutdown()

    def step(self, action):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state.
        Accepts an action and returns a tuple (observation, reward, done, info).
        Args:
            action (object): an action provided by the environment
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (bool): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        self._take_action(action)
        old_state = self.state
        eezybot.wait_for_shutdown()
        self.state = _get_current_state()
        if self.state is None:
            return (0, 0, 0), -1, True, {}
        reward = self._resolve_reward(old_state, self.state)
        self.episode_over = self._is_episode_over(self.state)
        return self.state, reward, self.episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """
        # Initial state
        eezybot.start().to_default_and_shutdown().wait_for_shutdown()
        return _get_current_state()

    def render(self, mode='human', close=False):
        """Renders the environment.
        The set of supported modes varies per environment. (And some
        environments do not support rendering at all.) By convention,
        if mode is:
        - human: render to the current display or terminal and
          return nothing. Usually for human consumption.
        - rgb_array: Return an numpy.ndarray with shape (x, y, 3),
          representing RGB values for an x-by-y pixel image, suitable
          for turning into a video.
        - ansi: Return a string (str) or StringIO.StringIO containing a
          terminal-style text representation. The text can include newlines
          and ANSI escape sequences (e.g. for colors).
        Note:
            Make sure that your class's metadata 'render.modes' key includes
              the list of supported modes. It's recommended to call super()
              in implementations to use the functionality of this method.
        Args:
            mode (str): the mode to render with
        """
        if self.image is not None:
            cv2.imshow('live view', self.image)
            cv2.waitKey(1)
        else:
            print("current state: {}".format(self.state))

    def close(self):
        """Override close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        eezybot.start().to_default_and_shutdown(interrupt=True).wait_for_shutdown()

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.
        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """
        return [seed]
