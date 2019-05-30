import h5py

filename = 'dqn_CartPole-v0_weights.h5f'

# does not do much for now
h5 = h5py.File(filename, 'r')
for key in list(h5.keys())[:-5]:
    print(h5[key])
