import logging

import gym
from gym.envs.registration import register

logger = logging.getLogger(__name__)


# delete if it's already registered
env_name = 'EezybotEnv-v0'
if env_name in gym.envs.registry.env_specs:
    del gym.envs.registry.env_specs[env_name]

env_name2 = 'OneServoEezybotEnv-v0'
if env_name2 in gym.envs.registry.env_specs:
    del gym.envs.registry.env_specs[env_name2]

env_name3 = 'SimpleEezybotEnv-v0'
if env_name3 in gym.envs.registry.env_specs:
    del gym.envs.registry.env_specs[env_name3]

register(
    id=env_name,
    entry_point='gym_eezybot.envs:eezybot_env',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic=True,
)

register(
    id=env_name2,
    entry_point='gym_eezybot.envs:one_servo_eezybot_env',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic=True,
)

register(
    id=env_name3,
    entry_point='gym_eezybot.envs:simple_eezybot_env',
    timestep_limit=1000,
    reward_threshold=1.0,
    nondeterministic=True,
)