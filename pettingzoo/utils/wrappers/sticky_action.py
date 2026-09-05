"""Wrappers that sometimes repeat an agent's previous action instead of the new one."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np
from gymnasium.utils import seeding
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _sticky_np_random(seed: int | None) -> np.random.Generator:
    """Builds an RNG that does not share a stream with the wrapped environment.

    ``seeding.np_random(seed)`` is a pure function of ``seed``, and nearly every
    PettingZoo environment calls it with the seed given to ``reset``. Using it
    directly here would hand the wrapper the same PCG64 stream the environment
    is drawing its own noise from, so the two would move in lockstep. Spawning a
    child sequence keeps the streams independent while staying reproducible.
    """
    # seeding.np_random validates the seed and, for seed=None, picks the entropy.
    _, np_seed = seeding.np_random(seed)
    child_seq = np.random.SeedSequence(np_seed).spawn(1)[0]
    return np.random.Generator(np.random.PCG64(child_seq))


class StickyActionV1(BaseWrapper[AgentID, ObsType, ActionType]):
    """Repeats an agent's previous action with probability ``repeat_action_probability``.

    Each agent keeps its own previous action, and an agent has nothing to repeat
    until it has acted once since the last :meth:`reset`, so the first action
    after a reset is always passed through. Only this wrapper's own reset clears
    the memory: an environment that auto-resets underneath it, such as
    ``MultiEpisodeParallelEnv`` on the inside, can still have the first action of
    a later episode repeated. The remembered action is a deep copy, so reusing an
    action buffer between steps does not defeat the wrapper.

    Seeding follows the usual PettingZoo pattern: :meth:`reset` reseeds from the
    seed it is given, which means ``reset(seed=None)`` starts a fresh unseeded
    stream. Pass a seed on every reset if you want a whole multi-episode run to
    be reproducible.

    :param env: The AEC environment to wrap.
    :param repeat_action_probability: Probability of using the previous action,
        in the interval [0, 1).
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        repeat_action_probability: float,
    ):
        assert isinstance(env, AECEnv), (
            "StickyActionV1 is only compatible with AEC environments, "
            "use StickyActionParallelV1 instead."
        )
        assert 0 <= repeat_action_probability < 1, (
            "repeat_action_probability must be in the interval [0, 1), "
            f"got {repeat_action_probability}."
        )
        super().__init__(env)
        self.repeat_action_probability = repeat_action_probability
        self._prev_actions: dict[AgentID, ActionType] = {}
        self._np_random = _sticky_np_random(None)

    def _sticky_action(self, agent: AgentID, action: ActionType) -> ActionType:
        if (
            agent in self._prev_actions
            and self._np_random.uniform() < self.repeat_action_probability
        ):
            # Hand out a copy so the environment cannot mutate what we remember.
            return copy.deepcopy(self._prev_actions[agent])
        self._prev_actions[agent] = copy.deepcopy(action)
        return action

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self._np_random = _sticky_np_random(seed)
        self._prev_actions = {}
        self.env.reset(seed=seed, options=options)

    @override
    def step(self, action: ActionType) -> None:
        # Read agent_selection defensively: it is missing before reset, and after
        # the last dead step it names an agent already dropped from terminations.
        agent = getattr(self.env, "agent_selection", None)
        if (
            agent is None
            or self.env.terminations.get(agent, True)
            or self.env.truncations.get(agent, True)
        ):
            # Stepping before reset, a dead agent's None step, or a step after
            # every agent is done. Nothing to stick, and the inner env owns the
            # error or warning.
            self.env.step(action)
            self._prev_actions.pop(agent, None)
        else:
            self.env.step(self._sticky_action(agent, action))

    @override
    def __str__(self) -> str:
        return f"StickyActionV1<{self.env!s}>"


class StickyActionParallelV1(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Repeats an agent's previous action with probability ``repeat_action_probability``.

    Each agent keeps its own previous action, and an agent has nothing to repeat
    until it has acted once since the last :meth:`reset`, so the first action
    after a reset is always passed through. Only this wrapper's own reset clears
    the memory: an environment that auto-resets underneath it, such as
    ``MultiEpisodeParallelEnv`` on the inside, can still have the first action of
    a later episode repeated. The remembered action is a deep copy, so reusing an
    action buffer between steps does not defeat the wrapper.

    Seeding follows the usual PettingZoo pattern: :meth:`reset` reseeds from the
    seed it is given, which means ``reset(seed=None)`` starts a fresh unseeded
    stream. Pass a seed on every reset if you want a whole multi-episode run to
    be reproducible.

    :param env: The parallel environment to wrap.
    :param repeat_action_probability: Probability of using the previous action,
        in the interval [0, 1).
    """

    def __init__(
        self,
        env: ParallelEnv[AgentID, ObsType, ActionType],
        repeat_action_probability: float,
    ):
        assert 0 <= repeat_action_probability < 1, (
            "repeat_action_probability must be in the interval [0, 1), "
            f"got {repeat_action_probability}."
        )
        super().__init__(env)
        self.repeat_action_probability = repeat_action_probability
        self._prev_actions: dict[AgentID, ActionType] = {}
        self._np_random = _sticky_np_random(None)

    def _sticky_action(self, agent: AgentID, action: ActionType) -> ActionType:
        if (
            agent in self._prev_actions
            and self._np_random.uniform() < self.repeat_action_probability
        ):
            # Hand out a copy so the environment cannot mutate what we remember.
            return copy.deepcopy(self._prev_actions[agent])
        self._prev_actions[agent] = copy.deepcopy(action)
        return action

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        self._np_random = _sticky_np_random(seed)
        self._prev_actions = {}
        return self.env.reset(seed=seed, options=options)

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
        actions = {
            agent: self._sticky_action(agent, action)
            for agent, action in actions.items()
        }
        observations, rewards, terminations, truncations, infos = self.env.step(actions)
        for agent in list(self._prev_actions):
            if terminations.get(agent, False) or truncations.get(agent, False):
                del self._prev_actions[agent]
        return observations, rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"StickyActionParallelV1<{self.env!s}>"
