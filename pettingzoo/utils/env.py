from pettingzoo.utils import EnvLogger


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

    def __getattr__(self, value):
        if value in {"rewards", "dones", "agent_selection"}:
            EnvLogger.error_field_before_reset(value)
            return None
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, value))
