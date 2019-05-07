import time
import gym
from gym import spaces
from scripts.detect_shapes import *
from scripts.constants import *
import eezybot_util

PRINT_DEBUG_MSGS = True

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

        # Live-view image
        self.image = None

        # Coordinate min/maxs
        self.min_input = 0
        self.max_input = 0

        # Discrete(n) is a set from 0 to n-1. We have n different actions our model can take.
        # Usually 8, each servo has 2 directions
        self.action_space = spaces.Discrete(3 * 2)

        # A R^n space which describes all valid inputs our model knows
        self.observation_space = spaces.Box(self.min_input, self.max_input, shape=(2,), dtype=np.float32)

        self.reward_range = (-float('inf'), float('inf'))
        self.episode_over = False

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

        # coords = detect_with_python2()

        self.image = cv2.imread('../images/pitest.jpg')
        if self.image is None:
            self.image = cv2.imread("images/pitest.jpg")

        coords = find_marbles(self.image)

        if PRINT_DEBUG_MSGS:
            print('found {} marbles at {}'.format(len(coords), coords))

            print("took {:1.0f} ms for calculations".format((time.time() - start_time) * 1000))
            print('----------------')

        self._take_action(action)
        reward = self._get_reward()
        ob = self._get_state()

        return ob, reward, self.episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """
        # targeted marble coords
        x, y = 0, 0

        distance = 0

        # Initial state
        self.state = ((x, y), distance)

        return np.array(self.state)

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

    """
    ----------- Own, non-api methods below here -----------
    """

    def _take_action(self, action):
        # action is which servo to move
        # 0,1 is servo 0 (+/-)
        # 2,3 is servo 1 (...)
        action = action // 2

        ll = [(1, 2, 3), (2, 3, 4)]
        a = [x for x in ll if x[2] == max([x[2] for x in ll])]

        # factor is in which direction to move
        # even numbers are positive direction
        factor = -1
        if action % 2 == 0:
            factor = 1

        eezybot_util.move(action, 1 * factor)

    def _get_state(self):
        """
                Get
                the
                observation.
        """
        ob = [self.TOTAL_TIME_STEPS - self.curr_step]
        return ob

    def _get_reward(self):
        """
        Reward is given
        for XY. """

        if "self.status" == "xyz":
            return 1
        elif "self.status" == "abc":
            return self.somestate ** 2
        else:
            return 0


if __name__ == '__main__':
    EezybotEnv().step(0)
