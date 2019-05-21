from eezybot_controller import eezybot
import ai_interface
import gym
from gym.envs.registration import register
import sys


def reinstall_env():
    from pip._internal import main as pipmain
    pipmain(['install', "-e", "./gym_/"])


def register_env():
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


if __name__ == '__main__':
    # -r arg to reinstall the gym env
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        reinstall_env()

    print('registering env...')
    register_env()

    while True:
        ai_interface.go_to_marble()
        eezybot.clutch.grab()
        ai_interface.go_to_destination()
        eezybot.clutch.release()
