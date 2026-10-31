"""Wrappers that repeat each supplied action for several underlying steps."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _is_positive_int(value: Any) -> bool:
    return (
        isinstance(value, (int, np.integer))
        and not isinstance(value, bool)
        and value >= 1
    )


class FrameSkipV1(BaseWrapper[AgentID, ObsType, ActionType]):
    """Repeats each agent's action for ``num_frames`` of that agent's turns.

    When an agent acts, its action is replayed on the agent's next
    ``num_frames - 1`` turns of the wrapped environment without asking the
    caller. Control returns to the caller as soon as the wrapped environment
    selects an agent that has no action left to replay, so the turn order the
    caller sees is the wrapped environment's own order. Rewards from every
    replayed turn are added up, and ``last()`` reports them as the agent's
    cumulative reward since it last acted.

    Actions are copied when submitted and on each replay, so caller or environment
    mutations cannot change the controls remembered for later turns.

    Agents that terminate or truncate while actions are being replayed are
    handed back to the caller for their usual ``step(None)``, and replaying
    continues after it. Their final observation is the wrapped environment's.
    Agents added during replaying appear in ``agents`` and get their first turn
    from the caller.

    ``num_frames=1`` leaves the environment unchanged. Unlike
    :class:`FrameSkipParallelV1`, only a fixed count is supported.

    :param env: The AEC environment to wrap.
    :param num_frames: Number of turns each supplied action is used for, at least 1.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], num_frames: int):
        assert isinstance(env, AECEnv), (
            "FrameSkipV1 is only compatible with AEC environments, "
            "use FrameSkipParallelV1 instead."
        )
        assert _is_positive_int(num_frames), (
            f"num_frames must be a positive integer, got {num_frames!r}."
        )
        super().__init__(env)
        self.num_frames = int(num_frames)
        self._actions: dict[AgentID, ActionType] = {}
        self._turns_left: dict[AgentID, int] = {}

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self.env.reset(seed=seed, options=options)
        self._actions = {}
        self._turns_left = {}
        self.rewards = dict.fromkeys(self.env.agents, 0.0)
        self._cumulative_rewards = dict.fromkeys(self.env.agents, 0.0)

    def _is_dead(self, agent: AgentID) -> bool:
        return self.env.terminations[agent] or self.env.truncations[agent]

    def _inner_step(self, agent: AgentID) -> None:
        action = copy.deepcopy(self._actions[agent])
        self._turns_left[agent] -= 1
        if self._turns_left[agent] == 0:
            del self._actions[agent]
            del self._turns_left[agent]
        self.env.step(action)
        for other, reward in self.env.rewards.items():
            self.rewards[other] = self.rewards.get(other, 0.0) + reward

    @override
    def step(self, action: ActionType) -> None:
        agent = self.env.agent_selection
        self._clear_rewards()
        if self._is_dead(agent):
            # The caller's step(None) for a dead agent; the wrapped env retires it.
            self.env.step(action)
        else:
            self._cumulative_rewards[agent] = 0.0
            self._actions[agent] = copy.deepcopy(action)
            self._turns_left[agent] = self.num_frames
            self._inner_step(agent)

        while self.env.agents:
            agent = self.env.agent_selection
            if self._is_dead(agent) or agent not in self._actions:
                break
            self._inner_step(agent)

        # Follow agents that were removed or added by the wrapped environment.
        agents = self.env.agents
        self._actions = {a: act for a, act in self._actions.items() if a in agents}
        self._turns_left = {a: n for a, n in self._turns_left.items() if a in agents}
        self.rewards = {a: self.rewards.get(a, 0.0) for a in agents}
        self._cumulative_rewards = {
            a: self._cumulative_rewards.get(a, 0.0) for a in agents
        }
        self._accumulate_rewards()


class FrameSkipParallelV1(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Repeats each step's actions for several steps of the wrapped environment.

    Each call to :meth:`step` steps the wrapped environment ``num_frames`` times
    with the same actions, or fewer if every agent is done earlier. Rewards are
    added up per agent. The observation, termination, truncation and info of each
    agent are the last ones the wrapped environment returned for it, so an agent
    that finishes partway through still reports its final transition.

    Each underlying step receives a fresh copy of each action, including the
    default action, so in-place changes cannot affect subsequent repeats.

    ``num_frames`` can also be a tuple ``(low, high)``. The number of steps is
    then drawn uniformly from ``low`` to ``high`` (inclusive) on every call, using
    the ``np_random`` generator of ``env.unwrapped``, which the environment seeds
    on ``reset(seed=...)``.

    An agent added by the wrapped environment partway through has no action
    from the caller yet, so it uses ``default_action`` until the next call to
    :meth:`step`. A ``ValueError`` is raised if that happens without a
    ``default_action``. Agents that are added and removed again within one call
    are not reported.

    :param env: The parallel environment to wrap.
    :param num_frames: Number of steps per call, at least 1, or a ``(low, high)``
        range with ``1 <= low <= high``.
    :param default_action: Action used for agents added partway through a call.
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        num_frames: int | tuple[int, int],
        default_action: ActionType | None = None,
    ):
        if isinstance(num_frames, tuple):
            assert (
                len(num_frames) == 2
                and all(_is_positive_int(n) for n in num_frames)
                and num_frames[0] <= num_frames[1]
            ), (
                "num_frames must be a positive integer or a tuple (low, high) "
                f"with 1 <= low <= high, got {num_frames!r}."
            )
            low, high = num_frames
        else:
            assert _is_positive_int(num_frames), (
                "num_frames must be a positive integer or a tuple (low, high) "
                f"with 1 <= low <= high, got {num_frames!r}."
            )
            low = high = num_frames
        super().__init__(env)
        self.num_frames = num_frames
        self.default_action = default_action
        self._low = int(low)
        self._high = int(high)

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
        if self._low == self._high:
            num_steps = self._low
        else:
            np_random = self.env.unwrapped.np_random  # ty: ignore[unresolved-attribute]
            num_steps = int(np_random.integers(self._low, self._high + 1))
        known_agents = set(self.env.agents) | set(actions)

        observations: dict[AgentID, ObsType] = {}
        rewards: dict[AgentID, float] = {}
        terminations: dict[AgentID, bool] = {}
        truncations: dict[AgentID, bool] = {}
        infos: dict[AgentID, dict[str, Any]] = {}

        for i in range(num_steps):
            obs, rews, terms, truncs, step_infos = self.env.step(
                {agent: copy.deepcopy(action) for agent, action in actions.items()}
            )
            observations.update(obs)
            terminations.update(terms)
            truncations.update(truncs)
            infos.update(step_infos)
            for agent, reward in rews.items():
                rewards[agent] = rewards.get(agent, 0.0) + reward

            if i == num_steps - 1 or not self.env.agents:
                break
            if all(terms[a] or truncs[a] for a in terms):
                break

            next_actions = {}
            for agent in self.env.agents:
                if agent in actions:
                    next_actions[agent] = actions[agent]
                elif self.default_action is not None:
                    next_actions[agent] = self.default_action
                else:
                    raise ValueError(
                        f"Agent {agent!r} was added partway through a "
                        "FrameSkipParallelV1 step and has no action yet. Pass "
                        "default_action to FrameSkipParallelV1 for such agents."
                    )
            actions = next_actions

        # The caller never saw agents that were added and removed in this call.
        final_agents = set(self.env.agents)
        for result in (observations, rewards, terminations, truncations, infos):
            for agent in list(result):
                if agent not in known_agents and agent not in final_agents:
                    del result[agent]

        return observations, rewards, terminations, truncations, infos
