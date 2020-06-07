class AECEnv(object):
    def __init__(self):
        pass

    def step(self, action, observe=True):
        raise NotImplementedError

    def reset(self, observe=True):
        raise NotImplementedError

    def observe(self, agent):
        raise NotImplementedError

    def last(self):
        agent = self.agent_selection
        return self.rewards[agent], self.dones[agent], self.infos[agent]

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass

    @property
    def agent_iter(self):
        return AECIterable(self)

class AECIterable:
    def __init__(self, env):
        self.env = env
    def __iter__(self):
        return AECIterator(self.env)

class AECIterator:
    def __init__(self, env):
        self.env = env
    def __next__(self):
        if all(self.env.dones.values()):
            raise StopIteration
        return self.env.agent_selection
