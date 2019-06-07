import gym
import numpy as np
from keras.layers import Dense, Activation, Flatten
from keras.models import Sequential
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy

from constants import AI


def train(dqn, env, steps):
    print('start learning...')
    dqn.fit(env, nb_steps=steps, visualize=True, verbose=2)

    # After training is done, we save the final weights.
    dqn.save_weights(AI.PROPERTIES.WEIGHTS_PATH, overwrite=True)
    print("saved weights")


class EezybotDQN:
    def __init__(self, do_training=True, create_new=False):
        # Get the environment and extract the number of actions.
        print('building gym...')
        env = gym.make(AI.PROPERTIES.ENV_NAME)
        np.random.seed(123)
        nb_actions = env.action_space.n

        print('initializing DQN...')
        # Next, we build a very simple model.
        model = Sequential()
        model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
        for layer_size in AI.PROPERTIES.LAYER_SIZES:
            model.add(Dense(layer_size))
            model.add(Activation('relu'))
        model.add(Dense(nb_actions))
        model.add(Activation('linear'))
        print(model.summary())
        if not create_new:
            try:
                model.load_weights(AI.PROPERTIES.WEIGHTS_PATH)
            except OSError:
                print("No saved weights found")
        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=500000, window_length=1)
        if create_new:
            policy = EpsGreedyQPolicy(eps=AI.PROPERTIES.ENTRY_EPSILON_FOR_NEW_AI)
            dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=AI.PROPERTIES.WARM_UP_STEPS,
                           target_model_update=1e-2, policy=policy)
            dqn.compile(Adam(lr=AI.PROPERTIES.LEARN_RATE), metrics=['mae'])
            if do_training:
                train(dqn, env, AI.PROPERTIES.ENTRY_STEPS_FOR_NEW_AI)
            else:
                # Finally, evaluate our algorithm for 5 episodes.
                dqn.test(env, nb_episodes=5, visualize=True)

        policy = EpsGreedyQPolicy(eps=AI.PROPERTIES.EPSILON)
        dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=AI.PROPERTIES.WARM_UP_STEPS,
                       target_model_update=1e-2, policy=policy)
        dqn.compile(Adam(lr=AI.PROPERTIES.LEARN_RATE), metrics=['mae'])
        # Okay, now it's time to learn something! We visualize the training here for show, but this
        # slows down training quite a lot. You can always safely abort the training prematurely using
        # Ctrl + C.
        if do_training:
            train(dqn, env, AI.PROPERTIES.STEPS)
        else:
            # Finally, evaluate our algorithm for 5 episodes.
            dqn.test(env, nb_episodes=AI.PROPERTIES.TEST_EPISODES, visualize=True)
