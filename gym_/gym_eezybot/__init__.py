import logging

import gym
from gym.envs.registration import register

logger = logging.getLogger(__name__)


# delete if it's already registered
env_name = 'EezybotEnv-v0'
if env_name in gym.envs.registry.env_specs:
    del gym.envs.registry.env_specs[env_name]

register(
    id=env_name,
    entry_point='gym_eezybot.envs:EezybotEnv',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic=True,
)
