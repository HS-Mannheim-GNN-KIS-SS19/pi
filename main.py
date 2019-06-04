import sys

import gym
from gym.envs.registration import register

import ai_interface
from eezybot_controller import eezybot


def register_env():
    # delete if it's already registered
    env_name = 'ComplexEezybotEnv-v0'
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
        entry_point='gym_eezybot.envs:ComplexEezybotEnv',
        timestep_limit=1000,
        reward_threshold=1.0,
        nondeterministic=True,
    )

    register(
        id=env_name2,
        entry_point='gym_eezybot.envs:OneServoEezybotEnv',
        timestep_limit=1000,
        reward_threshold=1.0,
        nondeterministic=True,
    )

    register(
        id=env_name3,
        entry_point='gym_eezybot.envs:SimpleEezybotEnv',
        timestep_limit=1000,
        reward_threshold=1.0,
        nondeterministic=True,
    )


if __name__ == '__main__':
    train = False
    new = False
    # -r arg to reinstall the gym env
    for i in range(len(sys.argv) - 1):
        if sys.argv[i + 1] == '-train' or sys.argv[i + 1] == '-t':
            train = True
        elif sys.argv[i + 1] == '-new' or sys.argv[i + 1] == '-n':
            new = True
        else:
            raise ValueError("There is no argument {} for main.py".format(sys.argv[i + 1]))

    print('registering env...')
    register_env()

    while True:
        ai_interface.go_to_marble(train, new)
        eezybot.clutch.start().grab().wait()
        eezybot.base.start().rotate(180).finish_and_shutdown()
        eezybot.verticalArm.start().to_default().finish_and_shutdown()
        eezybot.horizontalArm.start().to_default().finish_and_shutdown()
        eezybot.clutch.wait_for_servo(eezybot.base, eezybot.verticalArm,
                                      eezybot.horizontalArm).release().finish_and_shutdown()
        eezybot.join()
