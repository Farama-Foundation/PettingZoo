from typing import Any, Dict, List, Optional

import numpy as np
import pytest
from gymnasium import Space, spaces

from pettingzoo import AECEnv
from pettingzoo.utils import BaseWrapper

from pettingzoo.classic import go_v5, chess_v5


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


def simple_test():
    assert Env().last() == BaseWrapper(Env()).last()


def check_equal(last1, last2):
    if len(last1) != len(last2):
        return False
    if last1[0].keys() != last1[0].keys():
        return False
    for key in last1[0].keys():
        if not np.allclose(last1[0][key], last2[0][key]):
            return False

    if last1[1:] != last2[1:]:
        return False

    return True


@pytest.mark.parametrize("env_name", [go_v5, chess_v5])
def test_wrapped(env_name):
    env = env_name.env()
    env.reset()
    wrapped_env = BaseWrapper(env)
    assert check_equal(env.last(), wrapped_env.last())

    env.close()


@pytest.mark.parametrize("env_name", [go_v5, chess_v5])
def test_wrapped_play(env_name, play_rounds):
    env = env_name.env()
    env.reset()
    wrapped_env = BaseWrapper(env)
    for _ in range(play_rounds):
        observation, reward, termination, truncation, info = env.last()
        if termination or truncation:
            action = None
        else:
            action = env.action_space(env.agent_selection).sample(
                observation["action_mask"])  # this is where you would insert your policy
        env.step(action)
        check_equal(env.last(), wrapped_env.last())

    env.close()
