from __future__ import annotations

import warnings

import numpy as np
from gymnasium.spaces import Box, Discrete

from pettingzoo.test.api_test import test_observation_action_spaces as check_spaces
from pettingzoo.utils.env import AECEnv

AGENTS = ["player_0", "player_1"]
OBS_SPACE = Box(0, 1, shape=(2,), dtype=np.float32)


class DummyAEC(AECEnv):
    metadata = {"render_modes": [], "name": "dummy_spaces"}

    def __init__(self, action_spaces):
        super().__init__()
        self.possible_agents = list(AGENTS)
        self.agents = list(AGENTS)
        self._action_spaces = action_spaces
        self.agent_selection = self.agents[0]

    def observation_space(self, agent):
        return OBS_SPACE

    def action_space(self, agent):
        return self._action_spaces[agent]

    def reset(self, seed=None, options=None):
        pass

    def observe(self, agent):
        return np.zeros(2, np.float32)

    def step(self, action):
        pass


def _space_warnings(action_spaces):
    env = DummyAEC(action_spaces)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        check_spaces(env, env.agents[0])
    return [str(w.message) for w in caught]


def test_different_discrete_action_space_sizes_warn():
    msgs = _space_warnings({"player_0": Discrete(2), "player_1": Discrete(5)})
    assert any("action space sizes" in m for m in msgs)


def test_same_discrete_action_spaces_do_not_warn_size():
    msgs = _space_warnings({"player_0": Discrete(2), "player_1": Discrete(2)})
    assert not any("action space sizes" in m for m in msgs)


def test_different_action_space_classes_warn():
    msgs = _space_warnings(
        {
            "player_0": Discrete(2),
            "player_1": Box(0, 1, shape=(2,), dtype=np.float32),
        }
    )
    assert any("class of action spaces" in m for m in msgs)
