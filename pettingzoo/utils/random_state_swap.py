import numpy as np

class random_state_swap:
    '''
    usage:

    np_random, _ = gym.seeding.np_random(seed)
    with random_state_swap(np_random):
        # uses np_random's local random state
        r = np.random.normal(size=10)
        # can safely call external libraries which use np.random

    # uses np.random's global state
    r = np.random.normal(size=10)
    '''
    def __init__(self, rand_state):
        self.rand_state = rand_state.get_state()
    def __enter__(self):
        #ttysetattr etc goes here before opening and returning the file object
        self.old_np_state = np.random.get_state()
        np.random.set_state(self.rand_state)
        return None
    def __exit__(self, type, value, traceback):
        np.random.set_state(self.old_np_state)
