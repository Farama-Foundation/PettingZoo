"""Random rollout helpers must respect an action mask passed through ``info``.

api_test, seed_test, NanRandomWrapper and TerminateIllegalWrapper all accept the mask either in
``observation["action_mask"]`` or in ``info["action_mask"]``. These tests pin the same behaviour
for ``average_total_reward`` and ``random_demo``.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import gymnasium
import numpy as np
import pytest

from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import AgentSelector
from pettingzoo.utils.average_total_reward import average_total_reward
from pettingzoo.utils.random_demo import random_demo


class InfoMaskEnv(AECEnv[str, np.ndarray, int | None]):
    """Two agents, a plain Box observation, and a one-hot legal-action mask in ``info``.

    ``step`` raises on any action the mask forbids, so a rollout that ignores the mask fails loudly.
    """

    metadata = {"render_modes": [], "name": "info_mask_env"}
    num_actions = 4
    max_cycles = 5

    def __init__(self, start=0, mask_in_observation=False):
        super().__init__()
        self.possible_agents = ["player_0", "player_1"]
        self._obs_space = gymnasium.spaces.Box(0.0, 1.0, shape=(2,), dtype=np.float32)
        if mask_in_observation:
            self._obs_space = gymnasium.spaces.Dict(
                {
                    "observation": self._obs_space,
                    "action_mask": gymnasium.spaces.Box(
                        0, 1, (self.num_actions,), dtype=np.int8
                    ),
                }
            )
        self._act_space = gymnasium.spaces.Discrete(self.num_actions, start=start)
        self.mask_in_observation = mask_in_observation
        self.rng = np.random.default_rng(0)

    def observation_space(self, agent):
        return self._obs_space

    def action_space(self, agent):
        return self._act_space

    def observe(self, agent):
        observation = np.zeros(2, dtype=np.float32)
        if self.mask_in_observation:
            return {
                "observation": observation,
                "action_mask": self.infos[agent]["action_mask"],
            }
        return observation

    def _new_mask(self):
        return np.eye(self.num_actions, dtype=np.int8)[
            self.rng.integers(self.num_actions)
        ]

    def reset(self, seed=None, options=None):
        self.agents = self.possible_agents[:]
        self.rewards = dict.fromkeys(self.agents, 0)
        self._cumulative_rewards = dict.fromkeys(self.agents, 0)
        self.terminations = dict.fromkeys(self.agents, False)
        self.truncations = dict.fromkeys(self.agents, False)
        self.infos = {agent: {"action_mask": self._new_mask()} for agent in self.agents}
        self.num_steps = 0
        self._agent_selector = AgentSelector(self.agents)
        self.agent_selection = self._agent_selector.reset()

    def step(self, action):
        agent = self.agent_selection
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        assert self._act_space.contains(action), (
            f"{action} is outside {self._act_space}"
        )
        if not self.infos[agent]["action_mask"][action - self._act_space.start]:
            raise AssertionError(f"{agent} took masked-out action {action}")
        self._cumulative_rewards[agent] = 0
        self.rewards = dict.fromkeys(self.agents, 0)
        self.rewards[agent] = 1
        self.infos[agent] = {"action_mask": self._new_mask()}
        if self._agent_selector.is_last():
            self.num_steps += 1
            if self.num_steps >= self.max_cycles:
                self.truncations = dict.fromkeys(self.agents, True)
        self._accumulate_rewards()
        self.agent_selection = self._agent_selector.next()


@pytest.mark.parametrize(
    "rollout",
    [
        lambda env: average_total_reward(env, max_episodes=20),
        lambda env: random_demo(env, render=False, episodes=20),
    ],
    ids=["average_total_reward", "random_demo"],
)
@pytest.mark.parametrize("mask_in_observation", [False, True], ids=["info", "obs"])
@pytest.mark.parametrize("start", [0, 5, -5])
def test_random_rollout_honors_action_mask(rollout, start, mask_in_observation):
    with redirect_stdout(io.StringIO()):
        rollout(InfoMaskEnv(start=start, mask_in_observation=mask_in_observation))
