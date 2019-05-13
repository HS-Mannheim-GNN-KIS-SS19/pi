from enum import Enum

import cv2
import gym
from gym import spaces
import numpy as np
from image_processing_interface import get_arm, get_marbles, get_destination
from eezybot_servo_controller import eezybot
import raspi_camera


class Target(Enum):
    MARBLE = 0
    DESTINATION = 1
    FIXED_TARGET = 2


def _take_picture():
    return raspi_camera.take_picture()


class EezybotEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, kwargs):
        self.target_type = kwargs["target"]
        self.fixed_target = kwargs["is_fixed"]
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

        # Each action is a Tuple containing 3 angles.
        # Angle Range is 180 for every Servo with steps of 1 degree,
        # therefore 180**3 = 5832000 possible actions!!!!!!!!!!
        self.action_space = spaces.Discrete(180 ** 3)
        # A R^n space which describes all valid inputs our model knows
        self.observation_space = spaces.Box(self.min_distance_to_eezybot, self.max_distance_to_eezybot, shape=(4,),
                                            dtype=np.float32)

        self.reward_range = (-float('inf'), float('inf'))

        self.episode_over = False

        # Coordinate min/maxs
        # TODO: set to smallest/biggest distance from eezybot to marble
        self.min_distance_to_eezybot = 0
        self.max_distance_to_eezybot = int('inf')

        self.image = None
        self.state = None
        self.reset()

    def _resolve_target(self, image):
        if self.target_type is Target.FIXED_TARGET:
            return self.fixed_target
        elif self.target_type is Target.MARBLE:
            return get_marbles(image)[0]
        else:
            return get_destination(image)

    def _getCurrentState(self):
        self.image = _take_picture()
        return self._resolve_target(self.image), get_arm(self.image)

    """
    ----------- Api methods below here -----------
    """

    # TODO
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
        oldMarblePos, oldArmPos = self.state
        self.state = self._getCurrentState()
        marblePos, armPos = self.state
        reward = None

        return self.state, reward, self.episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """
        # Initial state
        eezybot.start.to_default_and_shutdown()
        return self._getCurrentState()

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
        eezybot.start.to_default_and_shutdown(interrupt=True)

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
