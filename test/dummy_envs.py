"""Two-agent envs shared by the wrapper tests.

Test modules subclass these and override ``observation_space`` and ``observe``.
"""

from __future__ import annotations

import functools

from gymnasium.spaces import Discrete

from pettingzoo.utils.env import AECEnv, ParallelEnv

AGENTS = ["agent_0", "agent_1"]


class DummyAEC(AECEnv):
    """Agents take turns, and all of them terminate after ``max_steps`` turns.

    The agent that just acted gets ``reward``. ``frame`` counts completed cycles,
    for tests whose observations change once per cycle like a real AEC env.
    """

    metadata = {"render_modes": [], "name": "dummy_aec"}
    max_steps = 8
    reward = 0.0

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0.0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {a: {} for a in self.agents}
        self._idx = 0
        self._step_count = 0
        self.frame = 0
        self.agent_selection = self.agents[0]

    def step(self, action):
        agent = self.agent_selection
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        self._step_count += 1
        self._cumulative_rewards[agent] = 0.0
        self.rewards = dict.fromkeys(self.agents, 0.0)
        self.rewards[agent] = self.reward
        if self._step_count >= self.max_steps:
            self.terminations = dict.fromkeys(self.agents, True)
        self._idx = (self._idx + 1) % len(self.agents)
        if self._idx == 0:
            self.frame += 1
        self.agent_selection = self.agents[self._idx]
        self._accumulate_rewards()

    def render(self):
        return None

    def close(self):
        pass


class DummyParallel(ParallelEnv):
    """All agents terminate after ``max_steps`` steps, getting ``reward`` on each.

    ``frame`` counts steps.
    """

    metadata = {"render_modes": [], "name": "dummy_parallel"}
    max_steps = 8
    reward = 0.0

    def __init__(self):
        super().__init__()
        self.possible_agents = list(AGENTS)

    @functools.cache
    def action_space(self, agent):
        return Discrete(2)

    def observe(self, agent):
        raise NotImplementedError

    def _observations(self):
        return {a: self.observe(a) for a in self.agents}

    def reset(self, seed=None, options=None):
        self.agents = list(self.possible_agents)
        self.frame = 0
        return self._observations(), {a: {} for a in self.agents}

    def step(self, actions):
        self.frame += 1
        done = self.frame >= self.max_steps
        obs = self._observations()
        rewards = dict.fromkeys(self.agents, self.reward)
        terminations = dict.fromkeys(self.agents, done)
        truncations = dict.fromkeys(self.agents, False)
        infos = {a: {} for a in self.agents}
        if done:
            self.agents = []
        return obs, rewards, terminations, truncations, infos

    def render(self):
        return None

    def close(self):
        pass
