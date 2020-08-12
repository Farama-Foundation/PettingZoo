from pettingzoo.utils.env import AECEnv

class ParallelEnv:
    def reset(self):
        '''
        returns:
        observations a dictionary {"agent_1":obs_1, ..., "agent_n": obs_n}
        '''

    def step(self, actions):
        '''
        parameters:
        - actions: {"agent_1": action1, ..., "agent_n": action_n}

        returns:
        (observations, rewards, dones, infos)

        steps all active agents in the environment, returns all observations, rewards, infos of those active agentts
        which are all dictionaries
        '''

    def render(self, mode="human"):
        '''
        renders environment by printing text or through a window
        '''

    def close(self):
        '''
        releases resources (typically just closes the rendering window)
        '''

class to_parallel(ParallelEnv):
    def __init__(self, aec_env):
        self.aec_env = aec_env
        self.observation_spaces = aec_env.observation_spaces
        self.action_spaces = aec_env.action_spaces
        self.agents = aec_env.agents

    def reset(self):
        self.aec_env.reset(observe=False)
        observations = {agent:self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations

    def step(self, actions):
        rewards = {}
        dones = {}
        infos = {}

        for agent in self.agents:
            if not self.aec_env.dones[agent]:
                assert agent == self.aec_env.agent_selection, f"environment has a nontrivial ordering, and cannot be used with the to_parallel wrapper\nCurrent agent: {self.aec_env.agent_selection}\nExpected agent: {agent}"
                self.aec_env.step(actions[agent], observe=False)
                rewards[agent] = self.aec_env.rewards[agent]
                dones[agent] = self.aec_env.dones[agent]
                infos[agent] = self.aec_env.infos[agent]

        observations = {agent:self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        return self.aec_env.render(mode)

    def close(self):
        return self.aec_env.close()

class from_parallel(AECEnv):
    def __init__(self, par_env):
        pass

    def step(self, action, observe=True):
        raise NotImplementedError

    def reset(self, observe=True):
        raise NotImplementedError

    def observe(self, agent):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        pass
