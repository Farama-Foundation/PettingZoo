from pettingzoo.utils import agent_selector
from pettingzoo import AECEnv
import copy


class _parallel_env_wrapper(AECEnv):

    def __init__(self, parallel_env):
        self.metadata = parallel_env.metadata
        self.env = parallel_env
        self.agents = self.env.agents[:]
        self.possible_agents = self.env.possible_agents

        self.action_spaces = self.env.action_spaces
        self.observation_spaces = self.env.observation_spaces

    def seed(self, seed=None):
        self.env.seed(seed)

    def reset(self, observe=True):
        self._observations = self.env.reset()
        self.agents = self.env.agents[:]
        self._live_agents = self.agents[:]
        self._actions = {agent: None for agent in self.agents}
        self._agent_selector = agent_selector(self._live_agents)
        self.agent_selection = self._agent_selector.reset()
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.rewards = {agent: 0 for agent in self.agents}


        return self.observe(self.agent_selection) if observe else None

    def observe(self, agent):
        return self._observations[agent]

    def step(self, action, observe=True):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action, observe)
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

            self._dones_step_first()
        else:
            self.agent_selection = self._agent_selector.next()
        return self.observe(self.agent_selection) if observe else None

    def render(self, mode="human"):
        return self.env.render(mode)

    def close(self):
        self.env.close()
