"""Wrappers that replace NaN actions with a random action from the agent's space."""

from __future__ import annotations

import copy
import warnings
from typing import Any

import gymnasium.spaces
import numpy as np
from gymnasium.spaces import Discrete
from gymnasium.utils import seeding
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _nan_random_np_random(seed: int | None) -> np.random.Generator:
    """Builds an RNG that does not share a stream with the wrapped environment.

    Environments usually seed themselves with ``seeding.np_random(seed)``, so
    this spawns a child sequence from the same seed, as ``StickyActionV1`` does.
    """
    _, np_seed = seeding.np_random(seed)
    child_seq = np.random.SeedSequence(np_seed).spawn(1)[0]
    return np.random.Generator(np.random.PCG64(child_seq))


def _action_mask(observation: Any, info: Any) -> Any:
    """Returns the agent's action mask, or ``None`` if it does not have one.

    A mask in a dictionary observation takes precedence over one in the info,
    the same order ``api_test`` uses when it samples masked actions.
    """
    if isinstance(observation, dict) and "action_mask" in observation:
        return observation["action_mask"]
    if isinstance(info, dict) and "action_mask" in info:
        return info["action_mask"]
    return None


def _random_action(
    space: gymnasium.spaces.Space[Any],
    mask: Any,
    agent: Any,
    np_random: np.random.Generator,
) -> Any:
    """Samples an action from ``space``, restricted to ``mask`` if there is one."""
    if mask is None:
        # Sample from a copy seeded by the wrapper, so the replacement neither
        # depends on nor advances the environment's own action space RNG.
        sample_space = copy.deepcopy(space)
        sample_space.seed(int(np_random.integers(2**32)))
        return sample_space.sample()

    if not isinstance(space, Discrete):
        raise ValueError(
            f"Agent {agent!r} has an action mask, but only Discrete action spaces "
            f"support masked NaN replacement, got {space}."
        )
    mask = np.asarray(mask)
    if mask.shape != (space.n,) or not np.isin(mask, (0, 1)).all():
        raise ValueError(
            f"The action mask for agent {agent!r} must contain only 0 and 1 and "
            f"have shape ({space.n},), got {mask!r}."
        )
    allowed = np.flatnonzero(mask)
    if allowed.size == 0:
        raise ValueError(f"The action mask for agent {agent!r} allows no actions.")
    return space.start + np_random.choice(allowed)


def _replace_nan(
    action: Any,
    space: gymnasium.spaces.Space[Any],
    mask: Any,
    agent: Any,
    np_random: np.random.Generator,
) -> Any:
    replacement = _random_action(space, mask, agent, np_random)
    warnings.warn(
        f"Step received a NaN action {action} for agent {agent!r}. "
        f"Taking the random action {replacement}.",
        stacklevel=3,
    )
    return replacement


def _has_nan(action: Any) -> bool:
    return action is not None and bool(np.isnan(action).any())


class NanRandomV1(BaseWrapper[AgentID, ObsType, Any]):
    """Replaces a numeric action containing a NaN with a random action.

    The replacement is sampled from the acting agent's action space, and a
    warning is emitted for each one. If the agent has an ``action_mask``, in its
    dictionary observation or else in its info, the replacement is drawn
    uniformly from the actions the mask allows. Masks are supported for
    ``Discrete`` action spaces; a mask on any other space, or one with the wrong
    shape, values other than 0 and 1, or no allowed action, raises a
    ``ValueError``.

    Numeric scalars and arrays are supported. Actions without NaNs, and ``None``
    actions for dead agents, pass through unchanged. The advertised action
    spaces are not modified.

    The random actions come from the wrapper's own RNG, which :meth:`reset`
    reseeds from the seed it is given, so a seeded reset gives reproducible
    replacements. As with ``StickyActionV1``, ``reset(seed=None)`` starts a fresh
    unseeded stream.

    :param env: The AEC environment to wrap.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "NanRandomV1 is only compatible with AEC environments, "
            "use NanRandomParallelV1 instead."
        )
        super().__init__(env)
        self._np_random = _nan_random_np_random(None)

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        self._np_random = _nan_random_np_random(seed)
        self.env.reset(seed=seed, options=options)

    @override
    def step(self, action: Any) -> None:
        if _has_nan(action):
            agent = self.env.agent_selection
            mask = _action_mask(self.env.observe(agent), self.env.infos.get(agent))
            action = _replace_nan(
                action, self.env.action_space(agent), mask, agent, self._np_random
            )
        self.env.step(action)

    @override
    def __str__(self) -> str:
        return f"NanRandomV1<{self.env!s}>"


class NanRandomParallelV1(BaseParallelWrapper[AgentID, ObsType, Any]):
    """Replaces each numeric action containing a NaN with a random action.

    Each supplied action is checked independently. A replacement is sampled from
    that agent's action space, restricted to its ``action_mask`` when the
    agent's latest dictionary observation or else its latest info has one, and a
    warning is emitted for each replacement. Masks follow the same rules as in
    :class:`NanRandomV1`.

    Numeric scalars and arrays are supported. Actions without NaNs pass through
    unchanged, and the input dictionary is not modified. The advertised action
    spaces are not modified. Seeding works as in :class:`NanRandomV1`.

    :param env: The parallel environment to wrap.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType]):
        super().__init__(env)
        self._np_random = _nan_random_np_random(None)
        self._observations: dict[AgentID, ObsType] = {}
        self._infos: dict[AgentID, dict[str, Any]] = {}

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        self._np_random = _nan_random_np_random(seed)
        self._observations, self._infos = self.env.reset(seed=seed, options=options)
        return self._observations, self._infos

    @override
    def step(
        self, actions: dict[AgentID, Any]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        replaced = {}
        for agent, action in actions.items():
            if _has_nan(action):
                mask = _action_mask(
                    self._observations.get(agent), self._infos.get(agent)
                )
                action = _replace_nan(
                    action, self.env.action_space(agent), mask, agent, self._np_random
                )
            replaced[agent] = action
        observations, rewards, terminations, truncations, infos = self.env.step(
            replaced
        )
        self._observations, self._infos = observations, infos
        return observations, rewards, terminations, truncations, infos

    @override
    def __str__(self) -> str:
        return f"NanRandomParallelV1<{self.env!s}>"
