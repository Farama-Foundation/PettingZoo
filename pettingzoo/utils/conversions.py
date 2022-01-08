import copy
import warnings
from collections import defaultdict

from pettingzoo.utils import agent_selector
from pettingzoo.utils.env import AECEnv, ParallelEnv
from pettingzoo.utils.wrappers import OrderEnforcingWrapper


def parallel_wrapper_fn(env_fn):
    def par_fn(**kwargs):
        env = env_fn(**kwargs)
        env = aec_to_parallel_wrapper(env)
        return env
    return par_fn


def aec_to_parallel(aec_env):
    if isinstance(aec_env, parallel_to_aec_wrapper):
        return aec_env.env
    else:
        par_env = aec_to_parallel_wrapper(aec_env)
        return par_env


def parallel_to_aec(par_env):
    if isinstance(par_env, aec_to_parallel_wrapper):
        return par_env.aec_env
    else:
        aec_env = parallel_to_aec_wrapper(par_env)
        ordered_env = OrderEnforcingWrapper(aec_env)
        return ordered_env


def to_parallel(aec_env):
    warnings.warn("The `to_parallel` function is deprecated. Use the `aec_to_parallel` function instead.")
    return aec_to_parallel(aec_env)


def from_parallel(par_env):
    warnings.warn("The `from_parallel` function is deprecated. Use the `parallel_to_aec` function instead.")
    return parallel_to_aec(par_env)


class aec_to_parallel_wrapper(ParallelEnv):
    def __init__(self, aec_env):
        assert aec_env.metadata.get('is_parallelizable', False), \
            "Converting from an AEC environment to a parallel environment " \
            "with the to_parallel wrapper is not generally safe " \
            "(the AEC environment should only update once at the end " \
            "of each cycle). If you have confirmed that your AEC environment " \
            "can be converted in this way, then please set the `is_parallelizable` "\
            "key in your metadata to True"

        self.aec_env = aec_env

        try:
            self.possible_agents = aec_env.possible_agents
        except AttributeError:
            pass

        self.metadata = aec_env.metadata

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.aec_env.state_space
        except AttributeError:
            pass

    @property
    def observation_spaces(self):
        warnings.warn("The `observation_spaces` dictionary is deprecated. Use the `observation_space` function instead.")
        try:
            return {agent: self.observation_space(agent) for agent in self.possible_agents}
        except AttributeError:
            raise AttributeError("The base environment does not have an `observation_spaces` dict attribute. Use the environments `observation_space` method instead")

    @property
    def action_spaces(self):
        warnings.warn("The `action_spaces` dictionary is deprecated. Use the `action_space` function instead.")
        try:
            return {agent: self.action_space(agent) for agent in self.possible_agents}
        except AttributeError:
            raise AttributeError("The base environment does not have an action_spaces dict attribute. Use the environments `action_space` method instead")

    def observation_space(self, agent):
        return self.aec_env.observation_space(agent)

    def action_space(self, agent):
        return self.aec_env.action_space(agent)

    @property
    def unwrapped(self):
        return self.aec_env.unwrapped

    def seed(self, seed=None):
        return self.aec_env.seed(seed)

    def reset(self):
        self.aec_env.reset()
        self.agents = self.aec_env.agents[:]
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations

    def step(self, actions):
        rewards = defaultdict(int)
        dones = {}
        infos = {}
        observations = {}
        for agent in self.aec_env.agents:
            if agent != self.aec_env.agent_selection:
                if self.aec_env.dones[agent]:
                    raise AssertionError(f"expected agent {agent} got done agent {self.aec_env.agent_selection}. Parallel environment wrapper expects all agent termination (setting an agent's self.dones entry to True) to happen only at the end of a cycle.")
                else:
                    raise AssertionError(f"expected agent {agent} got agent {self.aec_env.agent_selection}, Parallel environment wrapper expects agents to step in a cycle.")
            obs, rew, done, info = self.aec_env.last()
            self.aec_env.step(actions[agent])
            for agent in self.aec_env.agents:
                rewards[agent] += self.aec_env.rewards[agent]

        dones = dict(**self.aec_env.dones)
        infos = dict(**self.aec_env.infos)
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents}
        while self.aec_env.agents and self.aec_env.dones[self.aec_env.agent_selection]:
            self.aec_env.step(None)

        self.agents = self.aec_env.agents
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        return self.aec_env.render(mode)

    def state(self):
        return self.aec_env.state()

    def close(self):
        return self.aec_env.close()


class parallel_to_aec_wrapper(AECEnv):
    def __init__(self, parallel_env):
        self.env = parallel_env

        self.metadata = {**parallel_env.metadata}
        self.metadata['is_parallelizable'] = True

        try:
            self.possible_agents = parallel_env.possible_agents
        except AttributeError:
            pass

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.env.state_space
        except AttributeError:
            pass

    @property
    def unwrapped(self):
        return self.env.unwrapped

    @property
    def observation_spaces(self):
        warnings.warn("The `observation_spaces` dictionary is deprecated. Use the `observation_space` function instead.")
        try:
            return {agent: self.observation_space(agent) for agent in self.possible_agents}
        except AttributeError:
            raise AttributeError("The base environment does not have an `observation_spaces` dict attribute. Use the environments `observation_space` method instead")

    @property
    def action_spaces(self):
        warnings.warn("The `action_spaces` dictionary is deprecated. Use the `action_space` function instead.")
        try:
            return {agent: self.action_space(agent) for agent in self.possible_agents}
        except AttributeError:
            raise AttributeError("The base environment does not have an action_spaces dict attribute. Use the environments `action_space` method instead")

    def observation_space(self, agent):
        return self.env.observation_space(agent)

    def action_space(self, agent):
        return self.env.action_space(agent)

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
        self.new_agents = []
        self.new_values = {}

    def observe(self, agent):
        return self._observations[agent]

    def state(self):
        return self.env.state()

    def add_new_agent(self, new_agent):
        self._agent_selector._current_agent = len(self._agent_selector.agent_order)
        self._agent_selector.agent_order.append(new_agent)
        self.agent_selection = self._agent_selector.next()
        self.agents.append(new_agent)
        self.dones[new_agent] = False
        self.infos[new_agent] = {}
        self.rewards[new_agent] = 0
        self._cumulative_rewards[new_agent] = 0

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
            self._cumulative_rewards = copy.copy(rews)

            env_agent_set = set(self.env.agents)

            self.agents = self.env.agents + [agent for agent in sorted(self._observations.keys()) if agent not in env_agent_set]

            if len(self.env.agents):
                self._agent_selector = agent_selector(self.env.agents)
                self.agent_selection = self._agent_selector.reset()

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
