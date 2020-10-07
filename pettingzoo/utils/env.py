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

    def find_done(self):
        dones = self.dones
        return [agent for agent in self.agents if dones[agent]]

    def remove_if_done(self, agent):
        assert self.dones[agent], "an agent that was not done as attemted to be removed"
        del self.dones[agent]
        del self.rewards[agent]
        del self.infos[agent]
        self.agents.remove(agent)


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
