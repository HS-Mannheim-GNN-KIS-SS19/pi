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
    train = False
    new = False
    # -r arg to reinstall the gym env
    for i in range(len(sys.argv) - 1):
        if sys.argv[i + 1] == '-reset' or sys.argv[i + 1] == '-r':
            reinstall_env()
        elif sys.argv[i + 1] == '-train' or sys.argv[i + 1] == '-t':
            train = True
        elif sys.argv[i + 1] == '-new' or sys.argv[i + 1] == '-n':
            new = True
        else:
            raise ValueError("There is no argument {} for main.py".format(sys.argv[i + 1]))

    print('registering env...')
    register_env()

    while True:
        ai_interface.go_to_marble(train, new)
        eezybot.clutch.start().grab().shutdown().join()
        ai_interface.go_to_destination()
        eezybot.clutch.start().release().shutdown().join()
