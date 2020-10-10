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

    def _dones_step_first(self):
        dones = self.dones
        _dones_order = [agent for agent in self.agents if dones[agent]]
        if len(_dones_order):
            self._dones_iter = iter(_dones_order)
            self._skip_agent_selection = self.agent_selection
            self.agent_selection = next(self._dones_iter)

    def _find_next_agent(self):
        try:
            self.agent_selection = next(self._dones_iter)
        except StopIteration:
            if self.agents:
                self.agent_selection = self._skip_agent_selection

    def _remove_done_agent(self, agent):
        assert self.dones[agent], "an agent that was not done as attemted to be removed"
        del self.dones[agent]
        del self.rewards[agent]
        del self.infos[agent]
        self.agents.remove(agent)
        self.num_agents -= 1

    def _was_done_step(self, action, observe):
        if action is not None:
            raise ValueError("when an agent is done, the only valid action is None")
        self._remove_done_agent(self.agent_selection)
        self._find_next_agent()
        return self.observe(self.agent_selection) if observe else None

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
