from test.all_modules import all_environments
from typing import Any, Dict, List, Optional

import pytest
from gymnasium import Space, spaces

from pettingzoo import AECEnv
from pettingzoo.utils import BaseWrapper


class TestEnv(AECEnv):
    metadata = {"render.modes": ["ansi"], "name": "test_env"}

    def __init__(self, seed: Optional[int] = None):
        super().__init__()
        self.n_cards = 52
        self.cards = []

        self.possible_agents: List[str] = ["player_0"]
        self.agents = self.possible_agents.copy()

        self.action_spaces = {
            agent: spaces.Discrete(self.n_cards) for agent in self.agents
        }
        # The bug seems to be when using spaces.Sequence
        self.observation_spaces = {
            agent: spaces.Sequence(spaces.Discrete(self.n_cards))
            for agent in self.agents
        }
        self.infos = {i: {} for i in self.agents}

        self.reset(seed)

    def reset(
        self,
        seed: Optional[int] = None,
        return_info: bool = False,
        options: Optional[Dict] = None,
    ) -> None:
        self.cards = []

        self.agents = self.possible_agents.copy()
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.truncations = {i: False for i in self.agents}

    def seed(self, seed: Optional[int] = None) -> None:
        pass

    def observation_space(self, agent: str) -> Space:
        return self.observation_spaces[agent]

    def action_space(self, agent: str) -> Space:
        return self.action_spaces[agent]

    @property
    def agent_selection(self) -> str:
        return self.agents[0]

    @property
    def terminations(self) -> Dict[str, bool]:
        return {agent: False for agent in self.agents}

    def observe(self, agent: str) -> List[Any]:
        return self.cards

    def step(self, action: int) -> None:
        assert action in self.action_spaces[self.agent_selection]
        self.cards.append(action)

    def render(self) -> str:
        return self.cards.__repr__()

    def state(self):
        pass

    def close(self):
        super().close()


class TestEnvWrapper(BaseWrapper):
    def seed(self, seed: Optional[int] = None) -> None:
        pass


def test_wrapped():
    assert TestEnv().last() == TestEnvWrapper(TestEnv()).last()


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_all_envs_wrapped(name, env_module):
    _env = env_module.env(render_mode="human")
    assert _env.last() == TestEnvWrapper(_env).last()
