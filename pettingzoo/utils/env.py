import numpy as np
from typing import Optional


class AECEnv(object):
    def __init__(self):
        pass

    def step(self, action, observe=True) -> Optional[np.ndarray]:
        raise NotImplementedError

    def reset(self, observe=True) -> Optional[np.ndarray]:
        raise NotImplementedError

    def observe(self, agent) -> Optional[np.ndarray]:
        raise NotImplementedError

    def last(self):
        agent = self.agent_selection
        return self.rewards[agent], self.dones[agent], self.infos[agent]

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass
