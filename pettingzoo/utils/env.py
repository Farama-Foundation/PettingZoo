'''
Base environment definitions

See docs/api.md for api documentation
'''


class AECEnv:
    def __init__(self):
        pass

    def step(self, action, observe=True):
        raise NotImplementedError

    def reset(self, observe=True):
        raise NotImplementedError

    def seed(self, seed=None):
        raise NotImplementedError

    def observe(self, agent):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass


class ParallelEnv:
    def reset(self):
        raise NotImplementedError

    def seed(self, seed=None):
        raise NotImplementedError

    def step(self, actions):
        raise NotImplementedError

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        pass
