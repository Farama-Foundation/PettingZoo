"""Vectorized runners for PettingZoo Parallel environments."""

from __future__ import annotations

import multiprocessing as mp
import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any

import cloudpickle
import gymnasium.spaces
import numpy as np
from gymnasium.error import ClosedEnvironmentError
from gymnasium.vector import AutoresetMode, VectorEnv
from gymnasium.vector.utils import (
    batch_space,
    concatenate,
    create_empty_array,
    iterate,
)
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
    """Validate a ParallelEnv for homogeneous vectorized slot batching."""
    if not isinstance(env, ParallelEnv):
        raise TypeError(f"Expected a PettingZoo ParallelEnv, got {type(env).__name__}.")

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
    """Fetch the world's global state when supported, returning None otherwise."""
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
    """Ensure all possible_agents remain active, directing users to BlackDeathParallelV4."""
    active = list(env.agents)
    if len(active) != len(possible_agents) or set(active) != set(possible_agents):
        raise ValueError(
            f"Agent set changed during {phase} (expected {possible_agents}, got {active}). "
            "Wrap environments with BlackDeathParallelV4 when agents can depart early."
        )


def _resolve_autoreset_mode(autoreset_mode: str | AutoresetMode) -> AutoresetMode:
    """Normalize Gymnasium AutoresetMode enums and snake/pascal strings."""
    if isinstance(autoreset_mode, AutoresetMode):
        mode = autoreset_mode
    elif isinstance(autoreset_mode, str):
        normalized = autoreset_mode.strip().lower().replace("-", "_")
        if normalized in ("same_step", "samestep"):
            mode = AutoresetMode.SAME_STEP
        elif normalized in ("next_step", "nextstep"):
            mode = AutoresetMode.NEXT_STEP
        elif normalized == "disabled":
            mode = AutoresetMode.DISABLED
        else:
            raise ValueError(
                f"Unsupported autoreset_mode {autoreset_mode!r}; "
                "expected 'same_step' or 'next_step'."
            )
    else:
        raise TypeError(
            f"Expected AutoresetMode or str, got {type(autoreset_mode).__name__}."
        )
    if mode not in (AutoresetMode.SAME_STEP, AutoresetMode.NEXT_STEP):
        raise ValueError(
            f"Unsupported autoreset_mode {mode!r}; expected SAME_STEP or NEXT_STEP."
        )
    return mode


def _reset_world(
    env: ParallelEnv[Any, Any, Any],
    possible_agents: list[AgentID],
    has_state: bool,
    seed: int | None = None,
    options: dict[str, Any] | None = None,
) -> tuple[list[Any], list[dict[str, Any]], Any, bool]:
    """Reset one world and unpacks ordered agent observations and infos."""
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
    """Step one Parallel world and handles SAME_STEP / NEXT_STEP autoresets."""
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
    actions_dict = {agent: actions_slice[i] for i, agent in enumerate(possible_agents)}
    obs_dict, rew_dict, term_dict, trunc_dict, info_dict = env.step(actions_dict)
    if env.agents:
        _require_full_agent_set(env, possible_agents, phase="step()")

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
    """Recursively copy NumPy arrays inside nested Gymnasium space outputs."""
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
            raise ValueError(
                f"Expected at least 1 environment factory, got {num_worlds}."
            )

        mode = _resolve_autoreset_mode(autoreset_mode)

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
        self.closed = False

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
        """Concatenate per-world reset outputs into VectorEnv arrays and infos."""
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
        """Concatenate per-world step outputs, preserving final_obs and final_state."""
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
        """Split batched VectorEnv actions into per-world slices."""
        flat_actions = list(iterate(self.action_space, actions))
        if len(flat_actions) != self.num_envs:
            raise ValueError(
                f"Expected {self.num_envs} agent actions, got {len(flat_actions)}."
            )
        return [
            flat_actions[
                world_idx
                * self.agents_per_world : (world_idx + 1)
                * self.agents_per_world
            ]
            for world_idx in range(self.num_worlds)
        ]

    def states(self) -> Any:
        """Return batched CTDE global states across all ``num_worlds`` worlds."""
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
        self,
        name: str,
        *args: Any,
        world_indices: Sequence[int] | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        """Call a method or fetches an attribute value on selected Parallel worlds."""

    def get_attr(
        self, name: str, world_indices: Sequence[int] | None = None
    ) -> list[Any]:
        """Get an attribute or property from each selected Parallel world."""
        return self.call(name, world_indices=world_indices)

    def _ensure_open(self) -> None:
        """Raise ClosedEnvironmentError if the vector runner has already been closed."""
        if self.closed:
            raise ClosedEnvironmentError(
                f"Operation called on closed {self.__class__.__name__}."
            )

    def _resolve_reset_seeds(self, seed: int | list[int] | None) -> list[int | None]:
        """Expand an integer or sequence seed into per-world reset seeds."""
        if seed is None:
            return [None] * self.num_worlds
        if isinstance(seed, int):
            return [seed + idx for idx in range(self.num_worlds)]
        if len(seed) != self.num_worlds:
            raise ValueError(
                f"Expected {self.num_worlds} seeds (one per world), got {len(seed)}."
            )
        return list(seed)

    def _resolve_world_indices(self, world_indices: Sequence[int] | None) -> list[int]:
        """Normalize optional world indices with bounds validation."""
        if world_indices is None:
            return list(range(self.num_worlds))
        indices = list(world_indices)
        for idx in indices:
            if idx < 0 or idx >= self.num_worlds:
                raise IndexError(
                    f"World index {idx} out of range [0, {self.num_worlds})."
                )
        return indices


def _call_on_world(
    env: ParallelEnv[Any, Any, Any], name: str, *args: Any, **kwargs: Any
) -> Any:
    """Invoke a method or fetches an attribute on a single ParallelEnv."""
    target = getattr(env, name)
    if callable(target):
        return target(*args, **kwargs)
    if args or kwargs:
        raise TypeError(
            f"Attribute {name!r} on {env!s} is not callable, cannot pass arguments."
        )
    return target


_WorldSpec = tuple[
    list[AgentID],
    gymnasium.spaces.Space[Any],
    gymnasium.spaces.Space[Any],
    gymnasium.spaces.Space[Any] | None,
]

_StepWorldResult = tuple[
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


def _check_world_spec_match(
    expected: _WorldSpec, actual: _WorldSpec, world_idx: int
) -> None:
    """Ensure every world matches the reference agents and spaces."""
    exp_agents, exp_obs, exp_act, exp_state = expected
    act_agents, act_obs, act_act, act_state = actual
    if act_agents != exp_agents:
        raise ValueError(
            f"World {world_idx} possible_agents {act_agents} != {exp_agents}."
        )
    if act_obs != exp_obs:
        raise ValueError(f"World {world_idx} observation_space {act_obs} != {exp_obs}.")
    if act_act != exp_act:
        raise ValueError(f"World {world_idx} action_space {act_act} != {exp_act}.")
    if act_state != exp_state:
        raise ValueError(f"World {world_idx} state_space {act_state} != {exp_state}.")


def _verify_homogeneous_envs(
    envs: Sequence[ParallelEnv[Any, Any, Any]], world_offset: int = 0
) -> _WorldSpec:
    """Validate a sequence of worlds and ensures matching specs."""
    reference = _validate_world(envs[0])
    for local_idx, env in enumerate(envs[1:], start=1):
        _check_world_spec_match(
            reference, _validate_world(env), world_offset + local_idx
        )
    return reference


def _close_envs_quietly(envs: Sequence[Any]) -> None:
    """Close instantiated environments without masking prior initialization errors."""
    for env in envs:
        close_fn = getattr(env, "close", None)
        if callable(close_fn):
            try:
                close_fn()
            except Exception:
                pass


class SyncParallelVectorEnv(_BaseParallelVectorEnv):
    """Synchronous single-process vector runner for PettingZoo Parallel environments.

    Executes ``E`` homogeneous ``ParallelEnv`` instances sequentially in the main
    process while exposing standard Gymnasium ``VectorEnv`` ``(E * N, ...)`` arrays
    alongside CTDE ``states()`` and per-world ``call()`` inspection.
    """

    def __init__(
        self,
        env_fns: Sequence[Callable[[], ParallelEnv[Any, Any, Any]]],
        autoreset_mode: str | AutoresetMode = AutoresetMode.SAME_STEP,
        copy: bool = True,
    ) -> None:
        if not env_fns:
            raise ValueError("Expected at least 1 environment factory in 'env_fns'.")

        envs: list[ParallelEnv[Any, Any, Any]] = []
        try:
            for env_fn in env_fns:
                envs.append(env_fn())

            possible_agents, obs_space, act_space, state_space = (
                _verify_homogeneous_envs(envs)
            )
        except Exception:
            _close_envs_quietly(envs)
            raise

        self.env_fns = list(env_fns)
        self.envs = envs
        super().__init__(
            num_worlds=len(envs),
            possible_agents=possible_agents,
            single_obs_space=obs_space,
            single_act_space=act_space,
            single_state_space=state_space,
            env_metadata=getattr(envs[0], "metadata", {}),
            render_mode=getattr(envs[0], "render_mode", None),
            autoreset_mode=autoreset_mode,
            copy=copy,
        )

    @override
    def reset(
        self,
        *,
        seed: int | list[int] | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any]]:
        self._ensure_open()
        seeds = self._resolve_reset_seeds(seed)
        results = [
            _reset_world(
                env,
                self.possible_agents,
                self.has_state,
                seed=world_seed,
                options=options,
            )
            for env, world_seed in zip(self.envs, seeds)
        ]
        return self._collate_reset_results(results)

    @override
    def step(
        self, actions: Any
    ) -> tuple[Any, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        self._ensure_open()
        world_actions = self._split_world_actions(actions)
        results = [
            _step_world(
                env,
                self.possible_agents,
                world_actions[world_idx],
                self.autoreset_mode,
                self._needs_reset[world_idx],
                self.has_state,
            )
            for world_idx, env in enumerate(self.envs)
        ]
        return self._collate_step_results(results)

    @override
    def render(self) -> tuple[Any, ...]:
        self._ensure_open()
        return tuple(env.render() for env in self.envs)

    @override
    def call(
        self,
        name: str,
        *args: Any,
        world_indices: Sequence[int] | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        self._ensure_open()
        indices = self._resolve_world_indices(world_indices)
        return [
            _call_on_world(self.envs[idx], name, *args, **kwargs) for idx in indices
        ]

    @override
    def close_extras(self, **kwargs: Any) -> None:
        for env in self.envs:
            env.close()


def _shard_world_slices(num_worlds: int, num_workers: int | None) -> list[slice]:
    """Partition ``num_worlds`` evenly into contiguous slices across workers."""
    if num_worlds < 1:
        raise ValueError(f"Expected at least 1 world, got {num_worlds}.")
    if num_workers is None:
        effective = min(num_worlds, os.cpu_count() or 1)
    else:
        if num_workers < 1:
            raise ValueError(f"num_workers must be >= 1, got {num_workers}.")
        effective = min(num_worlds, num_workers)

    base, remainder = divmod(num_worlds, effective)
    slices: list[slice] = []
    start = 0
    for worker_idx in range(effective):
        stop = start + base + (1 if worker_idx < remainder else 0)
        slices.append(slice(start, stop))
        start = stop
    return slices


def _send_worker_error(pipe: Any, exc: Exception) -> None:
    """Send an exception over a pipe, falling back to RuntimeError if unpicklable."""
    try:
        pipe.send(("error", exc))
    except Exception:
        pipe.send(("error", RuntimeError(f"{type(exc).__name__}: {exc}")))


def _async_worker(
    pipe: Any,
    pickled_fns: bytes,
    autoreset_mode: AutoresetMode,
    world_offset: int,
) -> None:
    """Subprocess worker loop owning a contiguous shard of ParallelEnv worlds."""
    envs: list[ParallelEnv[Any, Any, Any]] = []
    try:
        env_fns = cloudpickle.loads(pickled_fns)
        envs = [fn() for fn in env_fns]
        spec = _verify_homogeneous_envs(envs, world_offset=world_offset)
        possible_agents, _, _, state_space = spec
        has_state = state_space is not None
        needs_reset = [False] * len(envs)
        metadata = dict(getattr(envs[0], "metadata", {}))
        render_mode = getattr(envs[0], "render_mode", None)
        pipe.send(("init_ok", cloudpickle.dumps((spec, metadata, render_mode))))
    except Exception as exc:
        _send_worker_error(pipe, exc)
        _close_envs_quietly(envs)
        pipe.close()
        return

    try:
        while True:
            try:
                cmd, payload = pipe.recv()
            except EOFError:
                break

            if cmd == "close":
                pipe.send(("ok", None))
                break

            try:
                if cmd == "reset":
                    world_seeds, options = payload
                    reset_results = []
                    for i, (env, w_seed) in enumerate(zip(envs, world_seeds)):
                        res = _reset_world(
                            env,
                            possible_agents,
                            has_state,
                            seed=w_seed,
                            options=options,
                        )
                        needs_reset[i] = res[-1]
                        reset_results.append(res)
                    pipe.send(("ok", reset_results))
                elif cmd == "step":
                    shard_actions = payload
                    step_results: list[_StepWorldResult] = []
                    for i, env in enumerate(envs):
                        res = _step_world(
                            env,
                            possible_agents,
                            shard_actions[i],
                            autoreset_mode,
                            needs_reset[i],
                            has_state,
                        )
                        needs_reset[i] = res[-1]
                        step_results.append(res)
                    pipe.send(("ok", step_results))
                elif cmd == "render":
                    pipe.send(("ok", tuple(env.render() for env in envs)))
                elif cmd == "call":
                    local_indices, name, pickled_args = payload
                    args, kwargs = cloudpickle.loads(pickled_args)
                    out = [
                        _call_on_world(envs[i], name, *args, **kwargs)
                        for i in local_indices
                    ]
                    pipe.send(("ok", out))
                else:
                    raise ValueError(f"Unknown worker command: {cmd!r}.")
            except Exception as exc:
                _send_worker_error(pipe, exc)
    finally:
        _close_envs_quietly(envs)
        pipe.close()


class AsyncParallelVectorEnv(_BaseParallelVectorEnv):
    """Multiprocess vector runner sharding Parallel environments across worker processes.

    Shards ``E`` homogeneous ``ParallelEnv`` instances evenly across ``num_workers``
    ``spawn``-safe worker processes (serialized with ``cloudpickle``) while preserving
    exact ``SyncParallelVectorEnv`` slot ordering, auto-reset behavior, ``states()``,
    and per-world ``call()`` semantics.
    """

    def __init__(
        self,
        env_fns: Sequence[Callable[[], ParallelEnv[Any, Any, Any]]],
        num_workers: int | None = None,
        autoreset_mode: str | AutoresetMode = AutoresetMode.SAME_STEP,
        copy: bool = True,
        context: str = "spawn",
    ) -> None:
        if not env_fns:
            raise ValueError("Expected at least 1 environment factory in 'env_fns'.")

        mode = _resolve_autoreset_mode(autoreset_mode)
        self.env_fns = list(env_fns)
        num_worlds = len(self.env_fns)
        self._world_slices = _shard_world_slices(num_worlds, num_workers)
        self.num_workers = len(self._world_slices)

        self._world_lookup: list[tuple[int, int]] = []
        for worker_idx, sl in enumerate(self._world_slices):
            for local_idx in range(sl.stop - sl.start):
                self._world_lookup.append((worker_idx, local_idx))

        mp_ctx = mp.get_context(context)
        self._parent_pipes: list[Any] = []
        self._processes: list[Any] = []
        self._pending_step = False

        try:
            worker_specs: list[tuple[_WorldSpec, dict[str, Any], str | None]] = []
            for sl in self._world_slices:
                parent_pipe, child_pipe = mp_ctx.Pipe()
                pickled_fns = cloudpickle.dumps(self.env_fns[sl])
                proc = mp_ctx.Process(
                    target=_async_worker,
                    args=(child_pipe, pickled_fns, mode, sl.start),
                    daemon=True,
                )
                proc.start()
                child_pipe.close()
                self._parent_pipes.append(parent_pipe)
                self._processes.append(proc)

            for pipe in self._parent_pipes:
                tag, payload = self._recv_packet(pipe)
                if tag != "init_ok":
                    raise RuntimeError(f"Unexpected worker handshake tag: {tag!r}.")
                worker_specs.append(cloudpickle.loads(payload))

            reference_spec, env_metadata, render_mode = worker_specs[0]
            for sl, (worker_spec, _, _) in zip(
                self._world_slices[1:], worker_specs[1:]
            ):
                _check_world_spec_match(reference_spec, worker_spec, sl.start)
        except Exception:
            self._shutdown_workers(timeout=2.0)
            raise

        possible_agents, obs_space, act_space, state_space = reference_spec
        super().__init__(
            num_worlds=num_worlds,
            possible_agents=possible_agents,
            single_obs_space=obs_space,
            single_act_space=act_space,
            single_state_space=state_space,
            env_metadata=env_metadata,
            render_mode=render_mode,
            autoreset_mode=mode,
            copy=copy,
        )

    def _recv_packet(self, pipe: Any) -> tuple[str, Any]:
        """Receive a message from a worker pipe or raises on worker crash."""
        try:
            tag, payload = pipe.recv()
        except (EOFError, BrokenPipeError) as exc:
            raise RuntimeError(
                "AsyncParallelVectorEnv worker process terminated unexpectedly."
            ) from exc
        if tag == "error":
            raise payload
        return tag, payload

    def _recv_ok(self, pipe: Any) -> Any:
        """Receive an ``('ok', value)`` response from a worker pipe."""
        tag, payload = self._recv_packet(pipe)
        if tag != "ok":
            raise RuntimeError(f"Unexpected worker message tag: {tag!r}.")
        return payload

    def _recv_all_ok(self, pipes: Sequence[Any]) -> list[Any]:
        """Drain every targeted pipe before raising the first worker error."""
        results: list[Any] = []
        first_error: Exception | None = None
        for pipe in pipes:
            try:
                results.append(self._recv_ok(pipe))
            except Exception as exc:
                if first_error is None:
                    first_error = exc
        if first_error is not None:
            raise first_error
        return results

    def _ensure_idle(self) -> None:
        """Ensure the runner is open and no ``step_async()`` is awaiting wait."""
        self._ensure_open()
        if self._pending_step:
            raise RuntimeError(
                "Operation disallowed while an async step is awaiting step_wait()."
            )

    @override
    def reset(
        self,
        *,
        seed: int | list[int] | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any]]:
        self._ensure_idle()

        seeds = self._resolve_reset_seeds(seed)
        for sl, pipe in zip(self._world_slices, self._parent_pipes):
            pipe.send(("reset", (seeds[sl], options)))

        results = []
        for worker_results in self._recv_all_ok(self._parent_pipes):
            results.extend(worker_results)
        return self._collate_reset_results(results)

    def step_async(self, actions: Any) -> None:
        """Dispatch batched actions to all worker processes without blocking."""
        self._ensure_idle()
        world_actions = self._split_world_actions(actions)
        for sl, pipe in zip(self._world_slices, self._parent_pipes):
            pipe.send(("step", world_actions[sl]))
        self._pending_step = True

    def step_wait(
        self,
    ) -> tuple[Any, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        """Wait for an in-flight ``step_async()`` and collates all world results."""
        self._ensure_open()
        if not self._pending_step:
            raise RuntimeError(
                "Cannot call step_wait() without a pending step_async()."
            )
        self._pending_step = False
        results: list[_StepWorldResult] = []
        for worker_results in self._recv_all_ok(self._parent_pipes):
            results.extend(worker_results)
        return self._collate_step_results(results)

    @override
    def step(
        self, actions: Any
    ) -> tuple[Any, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
        self.step_async(actions)
        return self.step_wait()

    @override
    def render(self) -> tuple[Any, ...]:
        self._ensure_idle()
        for pipe in self._parent_pipes:
            pipe.send(("render", None))
        frames: list[Any] = []
        for worker_frames in self._recv_all_ok(self._parent_pipes):
            frames.extend(worker_frames)
        return tuple(frames)

    @override
    def call(
        self,
        name: str,
        *args: Any,
        world_indices: Sequence[int] | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        self._ensure_idle()
        indices = self._resolve_world_indices(world_indices)
        if not indices:
            return []

        per_worker_reqs: dict[int, list[tuple[int, int]]] = {}
        for out_pos, world_idx in enumerate(indices):
            worker_idx, local_idx = self._world_lookup[world_idx]
            per_worker_reqs.setdefault(worker_idx, []).append((out_pos, local_idx))

        pickled_args = cloudpickle.dumps((args, kwargs))
        target_workers = list(per_worker_reqs.items())
        for worker_idx, pairs in target_workers:
            local_indices = [local_idx for _, local_idx in pairs]
            self._parent_pipes[worker_idx].send(
                ("call", (local_indices, name, pickled_args))
            )

        worker_outputs = self._recv_all_ok(
            [self._parent_pipes[worker_idx] for worker_idx, _ in target_workers]
        )
        outputs: list[Any] = [None] * len(indices)
        for (_, pairs), worker_out in zip(target_workers, worker_outputs):
            for (out_pos, _), val in zip(pairs, worker_out):
                outputs[out_pos] = val
        return outputs

    def _shutdown_workers(self, timeout: float = 5.0) -> None:
        """Close pipes and terminates worker subprocesses cleanly."""
        if getattr(self, "_pending_step", False):
            for pipe in getattr(self, "_parent_pipes", []):
                try:
                    pipe.recv()
                except Exception:
                    pass
            self._pending_step = False

        for pipe, proc in zip(
            getattr(self, "_parent_pipes", []), getattr(self, "_processes", [])
        ):
            if proc.is_alive():
                try:
                    pipe.send(("close", None))
                    pipe.recv()
                except Exception:
                    pass

        for proc in getattr(self, "_processes", []):
            proc.join(timeout=timeout)
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=1.0)

        for pipe in getattr(self, "_parent_pipes", []):
            try:
                pipe.close()
            except Exception:
                pass

        self._parent_pipes = []
        self._processes = []

    @override
    def close_extras(self, **kwargs: Any) -> None:
        timeout = float(kwargs.get("timeout", 5.0))
        self._shutdown_workers(timeout=timeout)

    def __del__(self) -> None:
        if not getattr(self, "closed", True):
            self.close()


__all__ = ["SyncParallelVectorEnv", "AsyncParallelVectorEnv"]
