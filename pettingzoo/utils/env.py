'''
Base environment definitions

See docs/api.md for api documentation
'''


class AECEnv:
    def __init__(self):
        pass

    def step(self, action):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def seed(self, seed=None):
        pass

    def observe(self, agent):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass

    @property
    def num_agents(self):
        return len(self.agents)

    @property
    def max_num_agents(self):
        return len(self.possible_agents)

    @property
    def env_done(self):
        return not self.agents

    def _dones_step_first(self):
        dones = self.dones
        _dones_order = [agent for agent in self.agents if dones[agent]]
        if len(_dones_order):
            self._dones_iter = iter(_dones_order)
            self._skip_agent_selection = self.agent_selection
            self.agent_selection = next(self._dones_iter)
        return self.agent_selection

    def _clear_rewards(self):
        for agent in self.rewards:
            self.rewards[agent] = 0

    def _accumulate_rewards(self):
        for agent, reward in self.rewards.items():
            self._cumulative_rewards[agent] += reward

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
        del self._cumulative_rewards[agent]
        del self.infos[agent]
        self.agents.remove(agent)

    def _was_done_step(self, action):
        if action is not None:
            raise ValueError("when an agent is done, the only valid action is None")
        self._remove_done_agent(self.agent_selection)
        self._find_next_agent()
        self._clear_rewards()

    def agent_iter(self, max_iter=2**63):
        return AECIterable(self, max_iter)

    def last(self, observe=True):
        agent = self.agent_selection
        observation = self.observe(agent) if observe else None
        return observation, self._cumulative_rewards[agent], self.dones[agent], self.infos[agent]


class AECIterable:
    def __init__(self, env, max_iter):
        self.env = env
        self.max_iter = max_iter

    def __iter__(self):
        return AECIterator(self.env, self.max_iter)


class AECIterator:
    def __init__(self, env, max_iter):
        self.env = env
        self.iters_til_term = max_iter
        self.env._is_iterating = True

    def __next__(self):
        if not self.env.agents or self.iters_til_term <= 0:
            raise StopIteration
        self.iters_til_term -= 1
        return self.env.agent_selection


class AECOrderEnforcingIterator(AECIterator):
    def __next__(self):
        agent = super().__next__()
        assert self.env._has_updated, "need to call step() or reset() in a loop over `agent_iter`!"
        self.env._has_updated = False
        return agent


class ParallelEnv:
    def reset(self):
        raise NotImplementedError

    def seed(self, seed=None):
        pass

    def step(self, actions):
        raise NotImplementedError

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        pass

    @property
    def num_agents(self):
        return len(self.agents)

    @property
    def max_num_agents(self):
        return len(self.possible_agents)

    @property
    def env_done(self):
        return not self.agents
