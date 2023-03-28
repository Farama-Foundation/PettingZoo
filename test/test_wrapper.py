from typing import Any, Dict, List, Optional

from gymnasium import Space, spaces

from pettingzoo import AECEnv
from pettingzoo.utils import BaseWrapper


class Env(AECEnv):
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


class EnvWrapper(BaseWrapper):
    def seed(self, seed: Optional[int] = None) -> None:
        pass


def test_wrapper():
    assert Env().last() == EnvWrapper(Env()).last()
    assert Env().last() == BaseWrapper(Env()).last()

    env = Env()
    assert env.last() == EnvWrapper(env).last()
    assert env.last() == BaseWrapper(env).last()
