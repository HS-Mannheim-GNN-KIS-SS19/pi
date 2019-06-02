import numpy as np

from constants import REWARD


def vector_length(vector):
    return np.math.sqrt(sum(i ** 2 for i in vector))


def distance_reward(old_state, new_state):
    return vector_length(new_state) - vector_length(old_state)


def radius_reward(old_r, new_r):
    return new_r - old_r


def resolve_rewards(old_state, new_state, rotation_successful):
    if new_state == (0, 0, 0) or not rotation_successful:
        return REWARD.FOR_FAILING
    d_reward = distance_reward(old_state[0:2], new_state[0:2])
    r_reward = radius_reward(old_state[2], new_state[2])
    reward = d_reward * REWARD.DISTANCE_MULTIPLIER + r_reward * REWARD.RADIUS_MULTIPLIER
    return reward, d_reward, r_reward
