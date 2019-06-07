import numpy as np

from constants import AI

REWARD = AI.PROPERTIES.REWARD


def vector_length(vector):
    return np.math.sqrt(sum(i ** 2 for i in vector))


def distance_reward(old_state, new_state):
    old = []
    new = []
    old.append(old_state[0])
    old.append(old_state[1]*2)
    new.append(new_state[0])
    new.append(new_state[1]*2)
    return -(vector_length(new) - vector_length(old))


def radius_reward(old_r, new_r):
    return new_r - old_r


def resolve_rewards(old_state, new_state, rotation_successful):
    if new_state == (0, 0, 0) or not rotation_successful:
        return REWARD.FOR_FAILING
    GRID_RADIUS = AI.PROPERTIES.ENV_PROPERTIES.INPUT_GRID_RADIUS
    if new_state[2] > 0.33 * GRID_RADIUS:
        return REWARD.FOR_SUCCESS
    d_reward = distance_reward(old_state[0:2], new_state[0:2])
    r_reward = radius_reward(old_state[2], new_state[2])
    reward = d_reward * REWARD.DISTANCE_MULTIPLIER + r_reward * REWARD.RADIUS_MULTIPLIER
    return reward, d_reward, r_reward
