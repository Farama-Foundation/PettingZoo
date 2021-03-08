from pettingzoo.utils import agent_selector
from pettingzoo.utils.env import AECEnv
import copy
from pettingzoo.utils.wrappers import OrderEnforcingWrapper
from pettingzoo.utils.env import ParallelEnv


def parallel_wrapper_fn(env_fn):
    def par_fn(**kwargs):
        env = env_fn(**kwargs)
        env = to_parallel_wrapper(env)
        return env
    return par_fn


def to_parallel(aec_env):
    if isinstance(aec_env, from_parallel_wrapper):
        return aec_env.env
    else:
        par_env = to_parallel_wrapper(aec_env)
        return par_env


def from_parallel(par_env):
    if isinstance(par_env, to_parallel_wrapper):
        return par_env.aec_env
    else:
        aec_env = from_parallel_wrapper(par_env)
        ordered_env = OrderEnforcingWrapper(aec_env)
        return ordered_env


class to_parallel_wrapper(ParallelEnv):
    def __init__(self, aec_env):
        self.aec_env = aec_env
        self.observation_spaces = aec_env.observation_spaces
        self.action_spaces = aec_env.action_spaces
        self.possible_agents = aec_env.possible_agents
        self.metadata = aec_env.metadata

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.aec_env.state_space
        except AttributeError:
            pass

    @property
    def unwrapped(self):
        return self.aec_env.unwrapped

    def seed(self, seed=None):
        return self.aec_env.seed(seed)

    def reset(self):
        self.aec_env.reset()
        self.agents = self.aec_env.agents
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations

    def step(self, actions):
        while self.aec_env.agents and self.aec_env.dones[self.aec_env.agent_selection]:
            self.aec_env.step(None)

        rewards = {a: 0 for a in self.aec_env.agents}
        dones = {}
        infos = {}
        observations = {}

        for agent in self.aec_env.agents:
            assert agent == self.aec_env.agent_selection, f"expected agent {agent} got agent {self.aec_env.agent_selection}, agent order is nontrivial"
            obs, rew, done, info = self.aec_env.last()
            self.aec_env.step(actions[agent])
            for agent in self.aec_env.agents:
                rewards[agent] += self.aec_env.rewards[agent]

        dones = dict(**self.aec_env.dones)
        infos = dict(**self.aec_env.infos)
        self.agents = self.aec_env.agents
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents}
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        return self.aec_env.render(mode)

    def state(self):
        return self.aec_env.state()

    def close(self):
        return self.aec_env.close()


class from_parallel_wrapper(AECEnv):
    def __init__(self, parallel_env):
        self.metadata = parallel_env.metadata
        self.env = parallel_env
        self.possible_agents = self.env.possible_agents

        self.action_spaces = self.env.action_spaces
        self.observation_spaces = self.env.observation_spaces

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.env.state_space
        except AttributeError:
            pass

    @property
    def unwrapped(self):
        return self.env.unwrapped

    def seed(self, seed=None):
        self.env.seed(seed)

    def reset(self):
        self._observations = self.env.reset()
        self.agents = self.env.agents[:]
        self._live_agents = self.agents[:]
        self._actions = {agent: None for agent in self.agents}
        self._agent_selector = agent_selector(self._live_agents)
        self.agent_selection = self._agent_selector.reset()
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}

    def observe(self, agent):
        return self._observations[agent]

    def state(self):
        return self.env.state()

    def step(self, action):
        if self.dones[self.agent_selection]:
            del self._actions[self.agent_selection]
            return self._was_done_step(action)
        self._actions[self.agent_selection] = action
        if self._agent_selector.is_last():
            obss, rews, dones, infos = self.env.step(self._actions)

            self._observations = copy.copy(obss)
            self.dones = copy.copy(dones)
            self.infos = copy.copy(infos)
            self.rewards = copy.copy(rews)
            self.agents = self.env.agents[:]

            self._live_agents = [agent for agent in self.agents if not dones[agent]]
            # assert self._live_agents == self.agents
            if len(self._live_agents):
                self._agent_selector = agent_selector(self._live_agents)
                self.agent_selection = self._agent_selector.reset()

            self._cumulative_rewards = copy.copy(rews)
            self._dones_step_first()
        else:
            if self._agent_selector.is_first():
                self._clear_rewards()

            self.agent_selection = self._agent_selector.next()

    def last(self, observe=True):
        agent = self.agent_selection
        observation = self.observe(agent) if observe else None
        return observation, self._cumulative_rewards[agent], self.dones[agent], self.infos[agent]

    def render(self, mode="human"):
        return self.env.render(mode)

    def close(self):
        self.env.close()

    def __str__(self):
        return str(self.env)
