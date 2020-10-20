from pettingzoo.utils import agent_selector
from pettingzoo import AECEnv


class _parallel_env_wrapper(AECEnv):

    def __init__(self, parallel_env):
        self.metadata = parallel_env.metadata
        self.env = parallel_env
        self.agents = self.env.agents
        self.possible_agents = self.env.possible_agents
        self.num_agents = len(self.agents)

        self.action_spaces = self.env.action_spaces
        self.observation_spaces = self.env.observation_spaces

    def seed(self, seed=None):
        self.env.seed(seed)

    def reset(self, observe=True):
        self.num_agents = len(self.possible_agents)
        self.agents = self.possible_agents[:]
        self._live_agents = self.agents[:]
        self._actions = {agent: None for agent in self.agents}
        self._agent_selector = agent_selector(self._live_agents)
        self.agent_selection = self._agent_selector.reset()
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.rewards = {agent: 0 for agent in self.agents}

        self._observations = self.env.reset()

        return self.observe(self.agent_selection) if observe else None

    def observe(self, agent):
        return self._observations[agent]

    def step(self, action, observe=True):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action, observe)
        self._actions[self.agent_selection] = action
        if self._agent_selector.is_last():
            obss, rews, dones, infos = self.env.step(self._actions)

            self._observations = obss
            self.dones = dones
            self.infos = infos
            self.rewards = rews

            self._live_agents = [agent for agent in self.agents if not dones[agent]]
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
