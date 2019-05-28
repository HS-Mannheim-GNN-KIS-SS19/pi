from constants import ENV
from image_processing_interface import get_state
import numpy as np


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
