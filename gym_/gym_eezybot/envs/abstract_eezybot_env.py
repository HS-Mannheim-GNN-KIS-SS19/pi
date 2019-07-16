from abc import ABC, abstractmethod

import gym
import matplotlib.pyplot as plt
import numpy as np
from gym import spaces
# noinspection PyUnresolvedReferences
from mpl_toolkits import mplot3d

from constants import AI
from eezybot_controller import eezybot
from image_processing_interface import get_state
from reward_calculation import resolve_rewards
from servo_controller import AngleTooLittleException, AngleTooBigException

env_properties = AI.properties.env
light_properties = AI.properties.light
visualize = AI.properties.visualize


class AbstractEezybotEnv(gym.Env, ABC):
    """DO NOT REGISTER AS ENV"""

    metadata = {'render.modes': ['human']}

    @abstractmethod
    def _map_action_to_angle_offset_tuple(self):
        pass

    @abstractmethod
    def __init__(self):
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
        # Should be 27 actions: 3 servos ^ 3 actions
        self.action_space = spaces.Discrete(env_properties.action_space_size)
        # A R^n space which describes all valid inputs our model knows (x, y, radius)
        self.observation_space = spaces.Box(-env_properties.input_data_type(env_properties.input_grid_radius),
                                            env_properties.input_data_type(env_properties.input_grid_radius),
                                            shape=(4,),
                                            dtype=env_properties.input_data_type)
        self.reward_range = (-float('inf'), float('inf'))
        if visualize:
            self.action = None

            self.x_states = []
            self.y_states = []
            self.rad_states = []

            self.d_reward = 0
            self.r_reward = 0
            self.reward = 0

            self.d_reward_sum_this_episode = 0
            self.r_reward_sum_this_episode = 0
            self.total_reward_sum_this_episode = 0

            self.average_d_reward_per_episode = []
            self.average_r_reward_per_episode = []
            self.average_reward_per_episode = []

            self.step_count_this_episode = 1
            self.step_count_per_episode = []

            self.successful_episode = False
            self.successful_episode_counter = 0

        self.action_tuples = self._map_action_to_angle_offset_tuple()
        self.state = None
        self.reset_position = None
        eezybot.start()

    def grab(self):
        eezybot.verticalArm.rotate(-10).wait()
        eezybot.horizontalArm.rotate(50)
        eezybot.clutch.grab().wait()
        eezybot.verticalArm.rotate_to_relative(1).wait()
        eezybot.base.rotate_to(np.random.randint(140) + 20)
        movement = np.random.randint(50)
        eezybot.horizontalArm.rotate_to_relative(1)
        eezybot.verticalArm.rotate_to(movement + 10)
        eezybot.clutch.wait_for_servo(eezybot.base, eezybot.verticalArm,
                                      eezybot.horizontalArm).release()

    def _is_episode_over(self, old_state, new_state, rotation_successful):
        if old_state == (0, 0, 0) and new_state == (0, 0, 0):
            return True
        if new_state[2] > light_properties.get_success_radius_by_grid_radius(1000) and -300 < new_state[0] < 300:
            if visualize:
                print("SUCCESS!!!")
                self.successful_episode = True
            self.reset_position = None
            self.showRewardsAndSteps()
            self.grab()
            return True
        return False

    def _take_action(self, action):
        base_angle, arm_vertical_angle, arm_horizontal_angle = self.action_tuples[action]
        rotation_successful = True
        rotation_state = 0
        try:
            if base_angle != 0:
                eezybot.base.rotate(base_angle, ensure_bounds=False)
        except AngleTooBigException as e:
            rotation_successful = False
            rotation_state = 1
            if visualize:
                print(e)
        except AngleTooLittleException as e:
            rotation_successful = False
            rotation_state = 2
            if visualize:
                print(e)
        try:
            if arm_vertical_angle != 0:
                eezybot.verticalArm.rotate(arm_vertical_angle, ensure_bounds=False)
        except AngleTooBigException as e:
            rotation_successful = False
            rotation_state = 3
            if visualize:
                print(e)
        except AngleTooLittleException as e:
            rotation_successful = False
            rotation_state = 4
            if visualize:
                print(e)
        try:
            if arm_horizontal_angle != 0:
                eezybot.horizontalArm.rotate(arm_horizontal_angle, ensure_bounds=False)
        except AngleTooBigException as e:
            rotation_successful = False
            rotation_state = 5
            if visualize:
                print(e)
        except AngleTooLittleException as e:
            rotation_successful = False
            rotation_state = 6
            if visualize:
                print(e)
        return rotation_successful, rotation_state

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
        rotation_successful, rotation_state = self._take_action(action)
        old_state = self.state
        eezybot.wait_for_all()
        self.state = get_state()
        episode_over = self._is_episode_over(old_state, self.state, rotation_successful)
        action = action
        reward, d_reward, r_reward = resolve_rewards(old_state, self.state, rotation_successful)
        eezybot.wait_for_all()
        if visualize:
            self.x_states.append(self.state[0])
            self.y_states.append(self.state[1])
            self.rad_states.append(self.state[2])

            self.action = action
            self.reward, self.d_reward, self.r_reward = reward, d_reward, r_reward
            if not self.successful_episode:
                self.total_reward_sum_this_episode += reward
                self.d_reward_sum_this_episode += d_reward
                self.r_reward_sum_this_episode += r_reward
                self.step_count_this_episode += 1

        return self.state + (rotation_state,), reward, episode_over, {}

    def reset(self):
        """Resets the state of the environment and returns an initial observation.
         Returns:
             observation (object): the initial observation.
         """

        if self.reset_position is None:
            eezybot.to_default().wait_for_all()
            self.state = self._search_marble()
        else:
            eezybot.base.rotate_to(self.reset_position)
            eezybot.verticalArm.to_default()
            eezybot.horizontalArm.to_default()
            eezybot.wait_for_all()
            self.state = get_state()

        if visualize and self.successful_episode:
            self.x_states.clear()
            self.y_states.clear()
            self.rad_states.clear()

            self.total_reward_sum_this_episode = 0
            self.d_reward_sum_this_episode = 0
            self.r_reward_sum_this_episode = 0
            self.step_count_this_episode = 1
            self.successful_episode = False
        return self.state + (0,)

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
        if visualize:
            print("current state: {}".format(self.state))
            print("Action: {}".format(self.action_tuples[self.action]))
            print("{} = d_reward: {} + r_reward: {}".format(self.reward, self.d_reward, self.r_reward))

    def close(self):
        """Override close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        eezybot.to_default_and_shutdown(dump_rotations=True).wait()

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

    def _search_marble(self):
        state = get_state()
        while state == (0, 0, 0):
            while state == (0, 0, 0) and eezybot.base.get_angle() < eezybot.base.max_degree - 20:
                eezybot.base.rotate(40).wait()
                state = get_state()
            while state == (0, 0, 0) and eezybot.base.get_angle() > eezybot.base.min_degree + 20:
                eezybot.base.rotate(-40).wait()
                state = get_state()
        self.reset_position = eezybot.base.get_angle()
        return state

    def showRewardsAndSteps(self):
        average_d_reward = self.d_reward_sum_this_episode / self.step_count_this_episode
        average_r_reward = self.r_reward_sum_this_episode / self.step_count_this_episode
        average_total_reward = self.total_reward_sum_this_episode / self.step_count_this_episode
        # print("Average Distance Reward this episode: {}".format(average_d_reward))
        # print("Average Radius Reward this episode: {}".format(average_r_reward))
        # print("Average Total Reward this episode: {}".format(average_total_reward))

        self.average_d_reward_per_episode.append(average_d_reward)
        self.average_r_reward_per_episode.append(average_r_reward)
        self.average_reward_per_episode.append(average_total_reward)
        self.step_count_per_episode.append(self.step_count_this_episode)
        self.successful_episode_counter += 1

        plt.figure(1)
        plt.subplot(211)
        # Data
        episodes = range(0, self.successful_episode_counter)
        # multiple line plot
        plt.plot(episodes, self.average_d_reward_per_episode, marker='o', markerfacecolor='gold', markersize=6,
                 color='yellow', linewidth=2, label='Distance Reward')
        plt.plot(episodes, self.average_r_reward_per_episode, marker='o', markerfacecolor='limegreen',
                 markersize=6, color='lawngreen', linewidth=2, label='Radius Reward')
        plt.plot(episodes, self.average_reward_per_episode, marker='o', markerfacecolor='blue', markersize=6,
                 color='skyblue', linewidth=2, label='Reward')
        plt.xticks(episodes)
        plt.xlabel('Episodes')
        plt.ylabel('Average Rewards')
        plt.legend()
        plt.subplot(212)
        plt.plot(episodes, self.step_count_per_episode, marker='o', markerfacecolor='red', markersize=6,
                 color='tomato', linewidth=2)
        plt.xticks(episodes)
        plt.xlabel('Episodes')
        plt.ylabel('Steps')
        plt.show()
        plt.figure(2)
        plt.plot(episodes, self.average_reward_per_episode, marker='o', markerfacecolor='blue', markersize=6,
                 color='skyblue', linewidth=2, label='Reward')
        plt.xticks(episodes)
        plt.xlabel('Episodes')
        plt.ylabel('Average Reward')
        plt.show()
        plt.figure(3)
        ax = plt.axes(projection='3d')
        ax.scatter3D(self.rad_states, self.x_states, self.y_states, cmap='hsv')
        ax.plot3D(self.rad_states, self.x_states, self.y_states, color='gray')
        ax.set_ylim3d(-600, 600)
        ax.set_ylabel('Horizontal')
        ax.set_xlim3d(0, 400)
        ax.set_xlabel('Radius')
        ax.set_zlim3d(-600, 600)
        ax.set_zlabel('Vertical')
        plt.show()
        plt.close('all')
