from abc import ABC, abstractmethod

import gym
from gym import spaces

from constants import EnvProperties
from eezybot_controller import eezybot
from image_processing import detect
from reward_calculation import *
from servo_controller import OutOfBoundsException


class AbstractEezybotEnv(gym.Env, ABC):
    """DO NOT REGISTER AS ENV"""

    metadata = {'render.modes': ['human']}

    @abstractmethod
    def _map_action_to_angle_offset_tuple(self):
        pass

    @abstractmethod
    def __init__(self, env_properties: EnvProperties):
        """The main OpenAI Gym class. It encapsulates an environment with
         arbitrary behind-the-scenes dynamics. An environment can be
         partially or fully observed.
         The main API methods that users of this class need to know are:
             step,
             reset,
             render,
             close,
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
        # TODO: Usage?
        self.min_distance_to_eezybot = 0
        self.max_distance_to_eezybot = float('inf')

        # Should be 27 actions: 3 servos ^ 3 actions
        self.action_space = spaces.Discrete(env_properties.action_space_size)
        # A R^n space which describes all valid inputs our model knows (x, y, radius)
        self.observation_space = spaces.Box(-env_properties.input_data_type(env_properties.input_grid_radius),
                                            env_properties.input_data_type(env_properties.input_grid_radius),
                                            shape=(3,),
                                            dtype=env_properties.input_data_type)
        self.reward_range = (-float('inf'), float('inf'))
        self.env_properties = env_properties
        self.action = None
        self.d_reward = None
        self.r_reward = None
        self.reward = None

        self.action_tuples = self._map_action_to_angle_offset_tuple()
        self.state = None
        self.reset()

    def grab(self):
        eezybot.verticalArm.start().rotate(
            eezybot.verticalArm.ensure_in_bounds(eezybot.verticalArm.get_rotation() + 20))
        eezybot.horizontalArm.start().rotate(eezybot.horizontalArm.max_degree)
        eezybot.clutch.start().grab().wait()
        eezybot.base.start().rotate_relative(1).finish_and_shutdown()
        eezybot.verticalArm.to_default().finish_and_shutdown()
        eezybot.horizontalArm.rotate_relative(0.5).finish_and_shutdown()
        eezybot.clutch.wait_for_servo(eezybot.base, eezybot.verticalArm,
                                      eezybot.horizontalArm).release().finish_and_shutdown()

    # TODO add reward for success
    def _is_episode_over(self, new_state, rotation_successful):
        if new_state == (0, 0, 0) or not rotation_successful or new_state[1] < 30:
            return True
        if env_properties.check_for_success_func():
            print("SUCCESSS!!!")
            self.grab()
            return True
        return False

    def _take_action(self, action):
        base_angle, arm_vertical_angle, arm_horizontal_angle = self.action_tuples[action]
        rotation_successful = True
        try:
            if base_angle != 0:
                eezybot.base.step(base_angle)
        except OutOfBoundsException as e:
            rotation_successful = False
            print(e)
        try:
            if arm_vertical_angle != 0:
                eezybot.verticalArm.step(arm_vertical_angle)
        except OutOfBoundsException as e:
            rotation_successful = False
            print(e)
        try:
            if arm_horizontal_angle != 0:
                eezybot.horizontalArm.step(arm_horizontal_angle)
        except OutOfBoundsException as e:
            rotation_successful = False
            print(e)
        eezybot.start().finish_and_shutdown()
        return rotation_successful

    def get_state(self):
        map = detect(*env_properties.target_color_space)
        marbles = map["marbles"]

        if marbles is None or len(marbles) == 0:
            return tuple([0, 0, 0])

        biggest = marbles[0]
        for i in range(len(marbles)):
            if marbles[i][2] > biggest[2]:
                biggest = marbles[i]

        scale = 2.0 / map["shape"][0]
        return tuple(
            [env_properties.input_data_type(
                (round(x * env_properties.input_grid_radius * scale + 1.0))) for x in biggest])

    if __name__ == '__main__':
        print(get_state())

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
        rotation_successful = self._take_action(action)
        old_state = self.state
        eezybot.join()
        self.state = self.get_state()
        episode_over = self._is_episode_over(self.state, rotation_successful)
        self.action = action
        self.reward, self.d_reward, self.r_reward = resolve_rewards(old_state, self.state, rotation_successful)
        eezybot.join()
        return self.state, self.reward, episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """

        eezybot.start().to_default_and_shutdown().join()
        self.state = self.get_state()
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
            close (bool): -
        """

        print("current state: {}".format(self.state))
        print("Action: {}".format(self.action_tuples[self.action]))
        print("{} = d_reward: {} + r_reward: {}".format(self.reward, self.d_reward, self.r_reward))

    def close(self):
        """Override close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        eezybot.start().to_default_and_shutdown(dump_rotations=True).join()

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
