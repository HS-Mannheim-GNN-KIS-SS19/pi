import numpy as np

from constants import AI

reward_properties = AI.properties.reward
env_properties = AI.properties.env


def vector_length(vector):
    return np.math.sqrt(sum(i ** 2 for i in vector))


def distance_reward(old_state, new_state):
    old = []
    new = []
    old.append(old_state[0] * reward_properties.multiplier.x)
    old.append(old_state[1] * reward_properties.multiplier.y)
    new.append(new_state[0] * reward_properties.multiplier.x)
    new.append(new_state[1] * reward_properties.multiplier.y)
    return -(vector_length(new) - vector_length(old))


def radius_reward(old_r, new_r):
    return new_r * reward_properties.multiplier.radius - old_r * reward_properties.multiplier.radius


def resolve_rewards(old_state, new_state, rotation_successful):
    if new_state == (0, 0, 0) or not rotation_successful or new_state[1] < 30:
        return reward_properties.for_failing
    if env_properties.check_for_success_func():
        return reward_properties.for_success
    d_reward = distance_reward(old_state[0:2], new_state[0:2])
    r_reward = radius_reward(old_state[2], new_state[2])
    reward = d_reward + r_reward
    return reward, d_reward, r_reward
