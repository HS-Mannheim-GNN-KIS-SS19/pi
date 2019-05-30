import numpy as np
import gym

from constants import AI
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


# Not sure about this
class EezybotRL:
    def __init__(self, train=True, create_new=False):
        print('building gym...')
        env = gym.make(AI.ENV_NAME)


class EezybotDQN:
    def __init__(self, train=True, create_new=False):
        # Get the environment and extract the number of actions.
        print('building gym...')
        env = gym.make(AI.ENV_NAME)

        np.random.seed(123)
        nb_actions = env.action_space.n

        print('initializing DQN...')
        # Next, we build a very simple model.
        model = Sequential()
        model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
        model.add(Dense(AI.LAYER_SIZE.FIRST // 4))
        model.add(Activation('relu'))
        model.add(Dense(AI.LAYER_SIZE.SECOND // 4))
        model.add(Activation('relu'))
        # model.add(Dense(AI.LAYER_SIZE.THIRD//2))
        # model.add(Activation('relu'))
        model.add(Dense(nb_actions))
        model.add(Activation('linear'))
        print(model.summary())
        if not create_new:
            try:
                model.load_weights(AI.FILEPATH)
            except OSError:
                print("No saved weights found")
        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=1000, window_length=1)
        policy = BoltzmannQPolicy()
        dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=30,
                       target_model_update=1e-2, policy=policy)

        dqn.compile(Adam(lr=AI.LEARN_RATE), metrics=['mae'])
        # Okay, now it's time to learn something! We visualize the training here for show, but this
        # slows down training quite a lot. You can always safely abort the training prematurely using
        # Ctrl + C.
        if train:
            print('start learning...')
            dqn.fit(env, nb_steps=AI.STEPS, visualize=True, verbose=2)

            # After training is done, we save the final weights.
            dqn.save_weights(AI.FILEPATH, overwrite=True)
            print("saved weights")
        else:
            # Finally, evaluate our algorithm for 5 episodes.
            dqn.test(env, nb_episodes=5, visualize=True)
