import time
import gym
from gym import spaces
import numpy as np
from image_processing import *
import eezybot_util
from constants import ENV


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
        # Representation of our models current state, initial state is set in reset()
        self.state = None

        self.last_distance = float('inf')

        # Live-view image
        self.image = None

        # Coordinate min/maxs
        # TODO: set to smallest/biggest distance from grip to marble
        self.min_input = 0
        self.max_input = 250

        # Discrete(n) is a set from 0 to n-1. We have n different actions our model can take.
        # Usually 6, each servo has 2 directions (not using clutch servo)
        self.action_space = spaces.Discrete(3 * 180)

        # A R^n space which describes all valid inputs our model knows
        self.observation_space = spaces.Box(self.min_input, self.max_input, shape=(4,), dtype=np.float32)

        self.reward_range = (-float('inf'), float('inf'))
        self.episode_over = False

        self.reset()

    def _take_action(self, action):
        # action is which servo to move
        # 0,1 is servo 0 (+/-)
        # 2,3 is servo 1 (...)
        action = action // 2

        # factor is in which direction to move
        # even numbers are positive direction
        factor = -1
        if action % 2 == 0:
            factor = 1

        eezybot_util.move_once(action, 1 * factor)

    """
    ----------- Api methods below here -----------
    """

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

        start_time = time.time()

        # move the arm
        self._take_action(action)

        coords = get_absolute_marble_positions(cv2.imread('../images/pitest.jpg'))

        if ENV.PRINT_DEBUG_MSGS:
            print('found {} marbles at {}'.format(len(coords), coords))

            print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
            print('----------------')

        # update state
        # take first found tuple for now
        x, y, z = coords[0]

        # distance is a tuple, 0 = distance horizontally, 1 = distance vertically
        distance = calculate_distance_to_arm(self.image)

        self.state = ((x, y, z), distance)

        # is done?
        self.episode_over = distance[0] < 1.0 and distance[1] < 1.0

        # calculate reward
        if abs(distance[0]) + abs(distance[1]) < abs(distance[0]) + abs(distance[1]):
            reward = 1.0
        else:
            reward = 0.0

        self.last_distance = distance

        return self.state, reward, self.episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """
        coords = get_absolute_marble_positions(cv2.imread('../images/pitest.jpg'))

        x, y, z = coords[0]

        # Initial state
        self.state = ((x, y, z), float('inf'))

        return self.state

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
        pass

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


if __name__ == '__main__':
    EezybotEnv().step(0)
