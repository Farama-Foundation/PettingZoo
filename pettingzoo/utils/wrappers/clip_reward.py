"""Wrappers that clip each agent's per-step reward into a closed interval."""

from __future__ import annotations

from typing import Any

from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _clip_reward(reward: float, min_reward: float, max_reward: float) -> float:
    if reward < min_reward:
        return min_reward
    if reward > max_reward:
        return max_reward
    return reward


class ClipRewardV1(BaseWrapper[AgentID, ObsType, ActionType]):
    """Clips each agent's per-step reward into ``[min_reward, max_reward]``.

    After every ``reset`` and ``step`` the inner ``rewards`` dict is clipped and
    the running total is rebuilt from that, so :meth:`~pettingzoo.utils.env.AECEnv.last`
    reports the sum of clipped steps. That is SuperSuit's ``clip_reward_v0``.

    :param env: The AEC environment to wrap.
    :param min_reward: Lower bound, inclusive. Default ``-1``.
    :param max_reward: Upper bound, inclusive. Default ``1``.
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        min_reward: float = -1,
        max_reward: float = 1,
    ):
        assert isinstance(env, AECEnv), (
            "ClipRewardV1 is only compatible with AEC environments, "
            "use ClipRewardParallelV1 instead."
        )
        assert min_reward <= max_reward, (
            f"min_reward ({min_reward}) must be <= max_reward ({max_reward})."
        )
        super().__init__(env)
        self.min_reward = min_reward
        self.max_reward = max_reward

    def _clip_and_accumulate(self, agent: AgentID | None = None) -> None:
        self.rewards = {
            a: _clip_reward(reward, self.min_reward, self.max_reward)
            for a, reward in self.env.rewards.items()
        }
        if agent is None:
            self._cumulative_rewards = dict.fromkeys(self.env._cumulative_rewards, 0.0)
        else:
            # Zero the agent that just stepped, matching SuperSuit, then add
            # this step's clipped rewards onto the running totals.
            self._cumulative_rewards[agent] = 0.0
        self._accumulate_rewards()

    @override
    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None):
        self.env.reset(seed=seed, options=options)
        self._clip_and_accumulate()

    @override
    def step(self, action: ActionType) -> None:
        agent = self.env.agent_selection
        self.env.step(action)
        self._clip_and_accumulate(agent)

    @override
    def __str__(self) -> str:
        return f"ClipRewardV1<{self.env!s}>"


class ClipRewardParallelV1(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Clips each agent's per-step reward into ``[min_reward, max_reward]``.

    SuperSuit's ``clip_reward_v0`` has no Parallel implementation of its own.
    This one clips the reward dict that :meth:`step` returns.

    :param env: The parallel environment to wrap.
    :param min_reward: Lower bound, inclusive. Default ``-1``.
    :param max_reward: Upper bound, inclusive. Default ``1``.
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        min_reward: float = -1,
        max_reward: float = 1,
    ):
        assert min_reward <= max_reward, (
            f"min_reward ({min_reward}) must be <= max_reward ({max_reward})."
        )
        super().__init__(env)
        self.min_reward = min_reward
        self.max_reward = max_reward

    def _clip(self, rewards: dict[AgentID, float]) -> dict[AgentID, float]:
        return {
            agent: _clip_reward(reward, self.min_reward, self.max_reward)
            for agent, reward in rewards.items()
        }

    @override
    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        observations, rewards, terminations, truncations, infos = self.env.step(actions)
        return observations, self._clip(rewards), terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"ClipRewardParallelV1<{self.env!s}>"
