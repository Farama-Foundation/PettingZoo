from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector


class DummyEnv(AECEnv):
    metadata = {"render_modes": ["human"], "is_parallelizable": True}

    def __init__(self, observations, observation_spaces, action_spaces):
        super().__init__()
        self._observations = observations
        self._observation_spaces = observation_spaces

        self.agents = sorted([x for x in observation_spaces.keys()])
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()
        self._action_spaces = action_spaces

        self.steps = 0

    def observation_space(self, agent):
        return self._observation_spaces[agent]

    def action_space(self, agent):
        return self._action_spaces[agent]

    def observe(self, agent):
        return self._observations[agent]

    def step(self, action, observe=True):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)
        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()
        self.steps += 1
        if self.steps >= 5 * len(self.agents):
            self.truncations = {a: True for a in self.agents}

        self._accumulate_rewards()
        self._deads_step_first()

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = {a: 1 for a in self.agents}
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.terminations = {a: False for a in self.agents}
        self.truncations = {a: False for a in self.agents}
        self.infos = {a: {} for a in self.agents}
        self.steps = 0

    def close(self):
        pass
