from __future__ import annotations

import pytest
from gymnasium.spaces import Discrete

from pettingzoo import AECEnv
from pettingzoo.utils import AgentSelector
from pettingzoo.utils.conversions import aec_to_parallel


class TwoAgentAECEnv(AECEnv):
    metadata = {"name": "two_agent_test", "is_parallelizable": True}
    render_mode = None

    def __init__(self, agents, truncated):
        self.possible_agents = list(agents)
        self.truncated = truncated
        self._space = Discrete(3)

    def observation_space(self, agent):
        return self._space

    def action_space(self, agent):
        return self._space

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.rewards = dict.fromkeys(self.agents, 0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0)
        self.infos = {agent: {"cycle": 0} for agent in self.agents}
        self.cycles = 0
        self._agent_selector = AgentSelector(self.agents)
        self.agent_selection = self._agent_selector.reset()

    def observe(self, agent):
        return self.cycles

    def step(self, action):
        agent = self.agent_selection
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return

        assert self.action_space(agent).contains(action)
        self._cumulative_rewards[agent] = 0
        self._clear_rewards()
        if self._agent_selector.is_last():
            self.cycles += 1
            self.rewards = {
                agent: self.cycles * (index + 1)
                for index, agent in enumerate(self.agents)
            }
            self.infos = {agent: {"cycle": self.cycles} for agent in self.agents}
            if self.cycles == 2:
                if self.truncated:
                    self.truncations = dict.fromkeys(self.agents, True)
                else:
                    self.terminations = dict.fromkeys(self.agents, True)
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()
        self._deads_step_first()


@pytest.mark.parametrize(
    "agents",
    [(0, 1), (("team", 0), ("team", 1)), ("player_0", "player_1")],
    ids=["integer", "tuple", "string"],
)
@pytest.mark.parametrize("truncated", [False, True], ids=["terminated", "truncated"])
def test_aec_to_parallel_preserves_agent_ids(agents, truncated):
    aec_env = TwoAgentAECEnv(agents, truncated)
    env = aec_to_parallel(aec_env)
    try:
        for _ in range(2):
            observations, infos = env.reset(seed=42)
            assert env.agents == list(agents)
            assert observations == dict.fromkeys(agents, 0)
            assert infos == {agent: {"cycle": 0} for agent in agents}
            assert infos is not aec_env.infos
            assert all(infos[agent] is aec_env.infos[agent] for agent in agents)

            for cycle in (1, 2):
                observations, rewards, terminations, truncations, infos = env.step(
                    dict.fromkeys(agents, 0)
                )
                assert observations == dict.fromkeys(agents, cycle)
                assert rewards == {
                    agent: cycle * (index + 1) for index, agent in enumerate(agents)
                }
                assert terminations == dict.fromkeys(
                    agents, cycle == 2 and not truncated
                )
                assert truncations == dict.fromkeys(agents, cycle == 2 and truncated)
                assert infos == {agent: {"cycle": cycle} for agent in agents}
                assert terminations is not aec_env.terminations
                assert truncations is not aec_env.truncations
                assert infos is not aec_env.infos
                if cycle == 1:
                    assert all(infos[agent] is aec_env.infos[agent] for agent in agents)
                    assert env.agents == list(agents)
                else:
                    assert env.agents == aec_env.agents == []
                    assert aec_env.terminations == aec_env.truncations == {}
                    assert aec_env.infos == {}
    finally:
        env.close()
