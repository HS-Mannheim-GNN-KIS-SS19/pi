import gym
from keras.layers import Dense, Activation, Flatten
from keras.models import Sequential
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy

from constants import AI

network = AI.properties.network
visualize = AI.properties.visualize


def train(dqn, env, steps):
    print('start learning...')
    history = dqn.fit(env, nb_steps=steps, visualize=True, verbose=2)
    # # for some reason this doesn't show anything
    # if visualize:
    #     print(history.history.keys())
    #     plt.plot(history.history['episode_reward'])

    # After training is done, we save the final weights.
    dqn.save_weights(network.weights_path[0] + str(network.weights_path[1] + 1) + '.h5f', overwrite=True)
    print("saved weights")


class EezybotDQN:
    def __init__(self, do_training=True, create_new=False):
        # Get the environment and extract the number of actions.
        print('building gym...')
        env = gym.make(AI.properties.env.type_name)
        # np.random.seed(123)
        # env.seed(123)
        nb_actions = env.action_space.n

        print('initializing DQN...')
        # Model building
        model = Sequential()
        model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
        for layer_size in network.layers:
            model.add(Dense(layer_size))
            model.add(Activation('relu'))
        model.add(Dense(nb_actions))
        model.add(Activation('linear'))
        if visualize:
            print(model.summary())
        if not create_new:
            try:
                model.load_weights(network.weights_path[0] + str(network.weights_path[1]) + '.h5f')
            except OSError:
                print("No saved weights found")
        memory = SequentialMemory(limit=500000, window_length=1)
        if do_training:
            for training in network.trainings:
                policy = EpsGreedyQPolicy(eps=training.epsilon)
                dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory,
                               nb_steps_warmup=training.warm_up_steps,
                               target_model_update=1e-2, policy=policy)
                dqn.compile(Adam(lr=training.learn_rate), metrics=['mae', 'accuracy'])
                train(dqn, env, training.steps)
        else:
            dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, target_model_update=1e-2)
            # Evaluate our algorithm for 5 episodes.
            dqn.compile(Adam(), metrics=['mae'])
            dqn.test(env, nb_episodes=5, visualize=True)
