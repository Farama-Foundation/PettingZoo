"""Vectorized runners for PettingZoo Parallel environments."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
import multiprocessing as mp
import os
from typing import Any

import cloudpickle
import gymnasium.spaces
from gymnasium.vector import AutoresetMode, VectorEnv
from gymnasium.vector.utils import batch_space, concatenate, create_empty_array, iterate
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


def _copy_tree(data: Any) -> Any:
    """Recursively copies NumPy arrays inside nested Gymnasium space outputs."""
    if isinstance(data, np.ndarray):
        return data.copy()
    if isinstance(data, dict):
        return {k: _copy_tree(v) for k, v in data.items()}
    if isinstance(data, tuple):
        return tuple(_copy_tree(v) for v in data)
    if isinstance(data, list):
        return [_copy_tree(v) for v in data]
    return data


class _BaseParallelVectorEnv(VectorEnv[Any, Any, Any], ABC):
    """Shared Gymnasium VectorEnv base for PettingZoo Parallel environments."""

    def __init__(
        self,
        num_worlds: int,
        possible_agents: list[AgentID],
        single_obs_space: gymnasium.spaces.Space[Any],
        single_act_space: gymnasium.spaces.Space[Any],
        single_state_space: gymnasium.spaces.Space[Any] | None,
        env_metadata: dict[str, Any],
        render_mode: str | None,
        autoreset_mode: str | AutoresetMode = AutoresetMode.SAME_STEP,
        copy: bool = True,
    ) -> None:
        super().__init__()
        if num_worlds < 1:
            raise ValueError(f"Expected at least 1 environment factory, got {num_worlds}.")

        mode = (
            autoreset_mode
            if isinstance(autoreset_mode, AutoresetMode)
            else AutoresetMode(autoreset_mode)
        )
        if mode not in (AutoresetMode.SAME_STEP, AutoresetMode.NEXT_STEP):
            raise ValueError(
                f"Unsupported autoreset_mode {mode!r}; expected SAME_STEP or NEXT_STEP."
            )

        self.num_worlds = int(num_worlds)
        self.possible_agents = list(possible_agents)
        self.agents_per_world = len(self.possible_agents)
        self.num_envs = self.num_worlds * self.agents_per_world
        self.autoreset_mode = mode
        self.copy = copy

        self.metadata = dict(env_metadata)
        self.metadata["autoreset_mode"] = self.autoreset_mode
        self.render_mode = render_mode

        self.single_observation_space = single_obs_space
        self.single_action_space = single_act_space
        self.observation_space = batch_space(single_obs_space, self.num_envs)
        self.action_space = batch_space(single_act_space, self.num_envs)

        self.single_state_space = single_state_space
        self.has_state = single_state_space is not None
        self.state_space = (
            batch_space(single_state_space, self.num_worlds)
            if single_state_space is not None
            else None
        )

        self._observations = create_empty_array(
            self.single_observation_space, n=self.num_envs, fn=np.zeros
        )
        self._rewards = np.zeros((self.num_envs,), dtype=np.float64)
        self._terminations = np.zeros((self.num_envs,), dtype=np.bool_)
        self._truncations = np.zeros((self.num_envs,), dtype=np.bool_)
        self._needs_reset = [False] * self.num_worlds
        self._latest_states: list[Any] = [None] * self.num_worlds

    def _collate_reset_results(
        self,
        world_results: Sequence[tuple[list[Any], list[dict[str, Any]], Any, bool]],
    ) -> tuple[Any, dict[str, Any]]:
        """Concatenates per-world reset outputs into VectorEnv arrays and infos."""
        flat_obs: list[Any] = []
        vector_infos: dict[str, Any] = {}

        for world_idx, (obs_list, info_list, state, needs_reset) in enumerate(
            world_results
        ):
            self._needs_reset[world_idx] = needs_reset
            self._latest_states[world_idx] = state
            flat_obs.extend(obs_list)
            base_slot = world_idx * self.agents_per_world
            for agent_offset, agent_info in enumerate(info_list):
                if agent_info:
                    vector_infos = self._add_info(
                        vector_infos, agent_info, base_slot + agent_offset
                    )

        concatenate(self.single_observation_space, flat_obs, self._observations)
        obs_out = _copy_tree(self._observations) if self.copy else self._observations
        return obs_out, vector_infos

    def _collate_step_results(
        self,
        world_results: Sequence[
            tuple[
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
            ]
        ],
    ) -> tuple[Any, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        """Concatenates per-world step outputs, preserving final_obs and final_state."""
        flat_obs: list[Any] = []
        vector_infos: dict[str, Any] = {}
        final_states: list[tuple[int, Any]] = []

        for world_idx, (
            obs_list,
            rew_list,
            term_list,
            trunc_list,
            info_list,
            state,
            final_obs,
            final_infos,
            final_state,
            needs_reset,
        ) in enumerate(world_results):
            self._needs_reset[world_idx] = needs_reset
            self._latest_states[world_idx] = state
            flat_obs.extend(obs_list)

            base_slot = world_idx * self.agents_per_world
            for agent_offset in range(self.agents_per_world):
                slot = base_slot + agent_offset
                self._rewards[slot] = rew_list[agent_offset]
                self._terminations[slot] = term_list[agent_offset]
                self._truncations[slot] = trunc_list[agent_offset]

                agent_info = info_list[agent_offset]
                if agent_info:
                    vector_infos = self._add_info(vector_infos, agent_info, slot)

                if final_obs is not None:
                    slot_final: dict[str, Any] = {"final_obs": final_obs[agent_offset]}
                    if final_infos is not None:
                        slot_final["final_info"] = final_infos[agent_offset]
                    vector_infos = self._add_info(vector_infos, slot_final, slot)

            if final_state is not None:
                final_states.append((world_idx, final_state))

        if final_states and self.single_state_space is not None:
            state_mask = np.zeros((self.num_worlds,), dtype=np.bool_)
            final_state_arr = np.full((self.num_worlds,), fill_value=None, dtype=object)
            for world_idx, f_state in final_states:
                final_state_arr[world_idx] = f_state
                state_mask[world_idx] = True
            vector_infos["final_state"] = final_state_arr
            vector_infos["_final_state"] = state_mask

        concatenate(self.single_observation_space, flat_obs, self._observations)
        if self.copy:
            return (
                _copy_tree(self._observations),
                self._rewards.copy(),
                self._terminations.copy(),
                self._truncations.copy(),
                vector_infos,
            )
        return (
            self._observations,
            self._rewards,
            self._terminations,
            self._truncations,
            vector_infos,
        )

    def _split_world_actions(self, actions: Any) -> list[list[Any]]:
        """Iterates batched VectorEnv actions into per-world slices."""
        flat_actions = list(iterate(self.action_space, actions))
        if len(flat_actions) != self.num_envs:
            raise ValueError(
                f"Expected {self.num_envs} agent actions, got {len(flat_actions)}."
            )
        return [
            flat_actions[
                world_idx * self.agents_per_world : (world_idx + 1) * self.agents_per_world
            ]
            for world_idx in range(self.num_worlds)
        ]

    def states(self) -> Any:
        """Returns batched CTDE global states across all ``num_worlds`` worlds."""
        if not self.has_state or self.single_state_space is None:
            raise NotImplementedError(
                "Wrapped ParallelEnv does not declare a Gymnasium 'state_space'."
            )
        if any(s is None for s in self._latest_states):
            raise RuntimeError(
                "Cannot call states() before reset() initializes all worlds."
            )
        out = create_empty_array(
            self.single_state_space, n=self.num_worlds, fn=np.zeros
        )
        concatenate(self.single_state_space, self._latest_states, out)
        return _copy_tree(out) if self.copy else out

    @abstractmethod
    def call(
        self, name: str, *args: Any, world_indices: Sequence[int] | None = None, **kwargs: Any
    ) -> list[Any]:
        """Calls a method or fetches an attribute value on selected Parallel worlds."""

    def get_attr(
        self, name: str, world_indices: Sequence[int] | None = None
    ) -> list[Any]:
        """Gets an attribute or property from each selected Parallel world."""
        return self.call(name, world_indices=world_indices)
