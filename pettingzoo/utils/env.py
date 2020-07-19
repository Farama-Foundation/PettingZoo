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
        raise NotImplementedError("last() has been removed. Please use final() instead.")

    def final(self):
        updates = [self.agent_selection]
        if hasattr(self,"_was_dones"):
            updates += [agent for agent in self.agents if self.dones[agent] and not self._was_dones[agent] and agent != self.agent_selection]
        self._was_dones = self.dones
        return [(agent, self.rewards[agent], self.dones[agent], self.infos[agent]) for agent in updates]

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass

    def agent_iter(self, max_agent_iter=2**63):
        return AECIterable(self, max_agent_iter)


class AECIterable:
    def __init__(self, env, max_agent_iter):
        self.env = env
        self.max_agent_iter = max_agent_iter

    def __iter__(self):
        if getattr(self.env, "_has_updated", None) is None:
            return AECIterator(self.env, self.max_agent_iter)
        else:
            return AECOrderEnforcingIterator(self.env, self.max_agent_iter)


class AECIterator:
    def __init__(self, env, max_agent_iter):
        self.env = env
        self.iters_til_term = max_agent_iter
        self._was_done = False

    def __next__(self):
        if self._was_done or self.iters_til_term <= 0:
            raise StopIteration
        self._was_done = all(self.env.dones.values())
        self.iters_til_term -= 1
        return self.env.agent_selection


class AECOrderEnforcingIterator(AECIterator):
    def __next__(self):
        assert self.env._has_updated, "need to call step() or reset() in a loop over `agent_iter`!"
        agent = super().__next__()
        self.env._has_updated = False
        return agent
