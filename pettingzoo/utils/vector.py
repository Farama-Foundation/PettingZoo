"""Vectorized runners for PettingZoo Parallel environments."""

from __future__ import annotations

from collections.abc import Callable, Sequence
import multiprocessing as mp
import os
from typing import Any

import cloudpickle
import gymnasium.spaces
from gymnasium.vector import AutoresetMode, VectorEnv
from gymnasium.vector.utils import batch_space, concatenate, iterate
import numpy as np
from typing_extensions import override

from pettingzoo.utils.env import AgentID, ParallelEnv


def _validate_world(
    env: ParallelEnv[Any, Any, Any],
) -> tuple[
    list[AgentID],
    gymnasium.spaces.Space[Any],
    gymnasium.spaces.Space[Any],
    gymnasium.spaces.Space[Any] | None,
]:
    """Validates a ParallelEnv for homogeneous vectorized slot batching."""
    if not isinstance(env, ParallelEnv):
        raise TypeError(
            f"Expected a PettingZoo ParallelEnv, got {type(env).__name__}."
        )

    possible_agents = list(getattr(env, "possible_agents", []))
    if not possible_agents:
        raise ValueError("ParallelEnv must define a non-empty 'possible_agents' list.")

    first_agent = possible_agents[0]
    obs_space = env.observation_space(first_agent)
    act_space = env.action_space(first_agent)

    for agent in possible_agents[1:]:
        if env.observation_space(agent) != obs_space:
            raise ValueError(
                "All agents must share an identical observation_space; "
                f"mismatch for agent {agent!r}: {env.observation_space(agent)} != {obs_space}."
            )
        if env.action_space(agent) != act_space:
            raise ValueError(
                "All agents must share an identical action_space; "
                f"mismatch for agent {agent!r}: {env.action_space(agent)} != {act_space}."
            )

    state_space = getattr(env, "state_space", None)
    if state_space is not None and not isinstance(state_space, gymnasium.spaces.Space):
        state_space = None

    return possible_agents, obs_space, act_space, state_space


def _snapshot_state(env: ParallelEnv[Any, Any, Any], has_state: bool) -> Any:
    """Fetches the world's global state when supported, returning None otherwise."""
    if not has_state:
        return None
    try:
        return env.state()
    except NotImplementedError:
        return None


def _require_full_agent_set(
    env: ParallelEnv[Any, Any, Any],
    possible_agents: list[AgentID],
    phase: str,
) -> None:
    """Ensures all possible_agents remain active, directing users to BlackDeathParallelV4."""
    active = list(env.agents)
    if len(active) != len(possible_agents) or set(active) != set(possible_agents):
        raise RuntimeError(
            f"Agent set changed during {phase} (expected {possible_agents}, got {active}). "
            "Wrap environments with BlackDeathParallelV4 when agents can depart early."
        )


def _reset_world(
    env: ParallelEnv[Any, Any, Any],
    possible_agents: list[AgentID],
    has_state: bool,
    seed: int | None = None,
    options: dict[str, Any] | None = None,
) -> tuple[list[Any], list[dict[str, Any]], Any, bool]:
    """Resets one world and unpacks ordered agent observations and infos."""
    obs_dict, info_dict = env.reset(seed=seed, options=options)
    _require_full_agent_set(env, possible_agents, phase="reset()")
    obs_list = [obs_dict[agent] for agent in possible_agents]
    info_list = [info_dict.get(agent, {}) for agent in possible_agents]
    state = _snapshot_state(env, has_state)
    return obs_list, info_list, state, False


def _step_world(
    env: ParallelEnv[Any, Any, Any],
    possible_agents: list[AgentID],
    actions_slice: Sequence[Any],
    autoreset_mode: AutoresetMode,
    needs_reset: bool,
    has_state: bool,
    autoreset_seed: int | None = None,
) -> tuple[
    list[Any],
    list[float],
    list[bool],
    list[bool],
    list[dict[str, Any]],
    Any,
    list[Any] | None,
    list[dict[str, Any]] | None,
    Any,
    bool,
]:
    """Steps one Parallel world and handles SAME_STEP / NEXT_STEP autoresets."""
    num_agents = len(possible_agents)

    if autoreset_mode == AutoresetMode.NEXT_STEP and needs_reset:
        obs_list, info_list, state, next_needs_reset = _reset_world(
            env, possible_agents, has_state, seed=autoreset_seed, options=None
        )
        return (
            obs_list,
            [0.0] * num_agents,
            [False] * num_agents,
            [False] * num_agents,
            info_list,
            state,
            None,
            None,
            None,
            next_needs_reset,
        )

    _require_full_agent_set(env, possible_agents, phase="step()")
    actions_dict = {
        agent: actions_slice[i] for i, agent in enumerate(possible_agents)
    }
    obs_dict, rew_dict, term_dict, trunc_dict, info_dict = env.step(actions_dict)

    obs_list = [obs_dict[agent] for agent in possible_agents]
    rew_list = [float(rew_dict[agent]) for agent in possible_agents]
    term_list = [bool(term_dict[agent]) for agent in possible_agents]
    trunc_list = [bool(trunc_dict[agent]) for agent in possible_agents]
    info_list = [info_dict.get(agent, {}) for agent in possible_agents]
    state = _snapshot_state(env, has_state)

    episode_done = (not env.agents) or all(
        term_list[i] or trunc_list[i] for i in range(num_agents)
    )

    if episode_done and autoreset_mode == AutoresetMode.SAME_STEP:
        final_obs = obs_list
        final_infos = info_list
        final_state = state
        obs_list, info_list, state, next_needs_reset = _reset_world(
            env, possible_agents, has_state, seed=autoreset_seed, options=None
        )
        return (
            obs_list,
            rew_list,
            term_list,
            trunc_list,
            info_list,
            state,
            final_obs,
            final_infos,
            final_state,
            next_needs_reset,
        )

    next_needs_reset = episode_done and autoreset_mode == AutoresetMode.NEXT_STEP
    return (
        obs_list,
        rew_list,
        term_list,
        trunc_list,
        info_list,
        state,
        None,
        None,
        None,
        next_needs_reset,
    )
