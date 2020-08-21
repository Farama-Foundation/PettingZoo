from pettingzoo.utils.env import AECEnv
from pettingzoo.utils._parallel_env import _parallel_env_wrapper
from pettingzoo.utils.wrappers import OrderEnforcingWrapper


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
        self.num_agents = aec_env.num_agents
        self._was_dones = {agent: False for agent in self.agents}

    def reset(self):
        self.aec_env.reset(observe=False)
        self._was_dones = {agent: False for agent in self.agents}
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations

    def step(self, actions):
        rewards = {}
        dones = {}
        infos = {}

        for agent in self.agents:
            if not self._was_dones[agent]:
                assert agent == self.aec_env.agent_selection, f"environment has a nontrivial ordering, and cannot be used with the to_parallel wrapper\nCurrent agent: {self.aec_env.agent_selection}\nExpected agent: {agent}"
                assert agent in actions, "Live environment agent is not in actions dictionary"
                self._was_dones[agent] = self.aec_env.dones[agent]
                self.aec_env.step(actions[agent], observe=False)
                agent = self.aec_env.agent_selection

        rewards = self.aec_env.rewards
        dones = self.aec_env.dones
        infos = self.aec_env.infos
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents}
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        return self.aec_env.render(mode)

    def close(self):
        return self.aec_env.close()


def parallel_wrapper_fn(env_fn):
    def par_fn(**kwargs):
        env = env_fn(**kwargs)
        env = to_parallel(env)
        return env
    return par_fn


class Sequentialize:
    def __init__(self, par_env):
        self.agents = par_env.agents
        self.observation_spaces = [par_env.observation_spaces[agent] for agent in self.agents]
        self.action_spaces = [par_env.action_spaces[agent] for agent in self.agents]
        self.par_env = par_env

    def _sequentialize(self, d):
        return [d.get(agent, None) for agent in self.agents]

    def reset(self):
        obs_dict = self.par_env.reset()

        return self._sequentialize(obs_dict)

    def step(self, actions):
        act_list = {agent: actions[i] for i, agent in enumerate(self.agents) if actions[i] is not None}
        obs, rew, done, info = self.par_env.step(act_list)
        obs = self._sequentialize(obs)
        rew = self._sequentialize(rew)
        done = self._sequentialize(done)
        info = self._sequentialize(info)
        return obs, rew, done, info

    def render(self, mode="human"):
        return self.par_env.render(mode)

    def close(self):
        self.par_env.close()


def from_parallel(par_env):
    if isinstance(par_env, to_parallel):
        return par_env.aec_env
    else:
        sequ_env = Sequentialize(par_env)
        aec_env = _parallel_env_wrapper(sequ_env)
        ordered_env = OrderEnforcingWrapper(aec_env)
        return ordered_env
