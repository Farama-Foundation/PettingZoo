from __future__ import annotations

import functools
from typing import Any

import numpy as np
import pytest
from gymnasium.error import ClosedEnvironmentError
from gymnasium.spaces import Box, Dict, Discrete
from gymnasium.vector import AutoresetMode

from pettingzoo.utils.env import ParallelEnv
from pettingzoo.utils.vector import AsyncParallelVectorEnv, SyncParallelVectorEnv
from pettingzoo.utils.wrappers import BlackDeathParallelV4


class CounterStateParallelEnv(ParallelEnv[str, np.ndarray, int]):
    """Minimal deterministic ParallelEnv with global state and configurable horizon."""

    metadata = {"name": "counter_state_parallel_v0", "render_modes": ["ansi"]}

    def __init__(
        self,
        world_tag: float = 0.0,
        horizon: int = 3,
        num_agents: int = 2,
        truncate_at_horizon: bool = False,
        obs_dim: int = 2,
        render_mode: str | None = "ansi",
    ) -> None:
        self.world_tag = float(world_tag)
        self.horizon = int(horizon)
        self.truncate_at_horizon = bool(truncate_at_horizon)
        self.obs_dim = int(obs_dim)
        self.render_mode = render_mode
        self.possible_agents = [f"agent_{idx}" for idx in range(num_agents)]
        self.agents: list[str] = []
        self.step_count = 0
        self.last_seed: int | None = None
        self.last_options: dict[str, Any] | None = None
        self.last_action_sum = 0.0
        self.state_space = Box(low=-1e6, high=1e6, shape=(3,), dtype=np.float32)

    @functools.cache
    def observation_space(self, agent: str) -> Box:
        return Box(low=-1e6, high=1e6, shape=(self.obs_dim,), dtype=np.float32)

    @functools.cache
    def action_space(self, agent: str) -> Discrete:
        return Discrete(3)

    def _make_obs(self) -> dict[str, np.ndarray]:
        return {
            agent: np.array(
                [
                    self.world_tag,
                    float(self.step_count * (idx + 1)),
                    *[0.0] * max(0, self.obs_dim - 2),
                ][: self.obs_dim],
                dtype=np.float32,
            )
            for idx, agent in enumerate(self.agents)
        }

    def state(self) -> np.ndarray:
        return np.array(
            [self.world_tag, float(self.step_count), self.last_action_sum],
            dtype=np.float32,
        )

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, dict[str, Any]]]:
        self.agents = list(self.possible_agents)
        self.step_count = 0
        self.last_seed = seed
        self.last_options = options
        self.last_action_sum = 0.0
        infos = {
            agent: {"seed": -1 if seed is None else seed, "step": 0}
            for agent in self.agents
        }
        return self._make_obs(), infos

    def step(
        self, actions: dict[str, int]
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        self.step_count += 1
        self.last_action_sum = float(sum(actions[a] for a in self.agents))
        done = self.step_count >= self.horizon
        term_flag = done and not self.truncate_at_horizon
        trunc_flag = done and self.truncate_at_horizon

        active = list(self.agents)
        obs = self._make_obs()
        rewards = {
            agent: float(actions[agent] + idx + 1) for idx, agent in enumerate(active)
        }
        terminations = dict.fromkeys(active, term_flag)
        truncations = dict.fromkeys(active, trunc_flag)
        infos = {
            agent: {"step": self.step_count, "world": int(self.world_tag)}
            for agent in active
        }
        if done:
            self.agents = []
        return obs, rewards, terminations, truncations, infos

    def ping(self, offset: int = 0) -> tuple[float, int]:
        return (self.world_tag, self.step_count + offset)

    def render(self) -> str:
        return f"world={int(self.world_tag)},step={self.step_count}"

    def close(self) -> None:
        pass


class NoStateParallelEnv(ParallelEnv[str, np.ndarray, int]):
    """ParallelEnv without a declared global state_space."""

    metadata = {"name": "no_state_parallel_v0"}

    def __init__(self) -> None:
        self.possible_agents = ["a0", "a1"]
        self.agents: list[str] = []

    @functools.cache
    def observation_space(self, agent: str) -> Box:
        return Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)

    @functools.cache
    def action_space(self, agent: str) -> Discrete:
        return Discrete(2)

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, dict[str, Any]]]:
        self.agents = list(self.possible_agents)
        return (
            {agent: np.zeros(2, dtype=np.float32) for agent in self.agents},
            {agent: {} for agent in self.agents},
        )

    def step(
        self, actions: dict[str, int]
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        active = list(self.agents)
        return (
            {agent: np.ones(2, dtype=np.float32) for agent in active},
            dict.fromkeys(active, 1.0),
            dict.fromkeys(active, False),
            dict.fromkeys(active, False),
            {agent: {} for agent in active},
        )


class EarlyDepartureParallelEnv(ParallelEnv[str, np.ndarray, int]):
    """ParallelEnv where agent_0 exits early on step 1 while agent_1 runs to step 2."""

    metadata = {"name": "early_departure_vec_v0"}

    def __init__(self) -> None:
        self.possible_agents = ["agent_0", "agent_1"]
        self.agents: list[str] = []
        self.step_count = 0

    @functools.cache
    def observation_space(self, agent: str) -> Box:
        return Box(low=-10.0, high=10.0, shape=(2,), dtype=np.float32)

    @functools.cache
    def action_space(self, agent: str) -> Discrete:
        return Discrete(2)

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, dict[str, Any]]]:
        self.agents = list(self.possible_agents)
        self.step_count = 0
        return (
            {agent: np.zeros(2, dtype=np.float32) for agent in self.agents},
            {agent: {} for agent in self.agents},
        )

    def step(
        self, actions: dict[str, int]
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        self.step_count += 1
        if self.step_count == 1:
            obs = {
                "agent_0": np.array([1.0, 0.0], dtype=np.float32),
                "agent_1": np.array([0.0, 1.0], dtype=np.float32),
            }
            rew = {"agent_0": -1.0, "agent_1": 1.0}
            term = {"agent_0": True, "agent_1": False}
            trunc = {"agent_0": False, "agent_1": False}
            info = {"agent_0": {}, "agent_1": {}}
            self.agents = ["agent_1"]
            return obs, rew, term, trunc, info

        obs = {"agent_1": np.array([2.0, 2.0], dtype=np.float32)}
        rew = {"agent_1": 3.0}
        term = {"agent_1": True}
        trunc = {"agent_1": False}
        info = {"agent_1": {}}
        self.agents = []
        return obs, rew, term, trunc, info


def _make_runner(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
    env_fns: list[Any],
    *,
    autoreset_mode: str | AutoresetMode = AutoresetMode.SAME_STEP,
    num_workers: int = 2,
) -> SyncParallelVectorEnv | AsyncParallelVectorEnv:
    if runner_cls is AsyncParallelVectorEnv:
        return AsyncParallelVectorEnv(
            env_fns,
            num_workers=num_workers,
            autoreset_mode=autoreset_mode,
            context="spawn",
        )
    return SyncParallelVectorEnv(env_fns, autoreset_mode=autoreset_mode)


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_spaces_slot_ordering_and_seeding(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    env_fns = [lambda w=w: CounterStateParallelEnv(world_tag=w) for w in range(3)]
    vec = _make_runner(runner_cls, env_fns)
    try:
        assert vec.num_worlds == 3
        assert vec.agents_per_world == 2
        assert vec.num_envs == 6
        assert vec.metadata["autoreset_mode"] == AutoresetMode.SAME_STEP
        assert vec.observation_space.shape == (6, 2)
        assert vec.single_observation_space.shape == (2,)
        assert vec.action_space.shape == (6,)
        assert vec.has_state
        assert vec.state_space is not None
        assert vec.state_space.shape == (3, 3)

        with pytest.raises(RuntimeError, match="before reset"):
            vec.states()

        obs, infos = vec.reset(seed=100)
        assert obs.shape == (6, 2)
        expected_tags = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0], dtype=np.float32)
        np.testing.assert_allclose(obs[:, 0], expected_tags)
        np.testing.assert_array_equal(infos["seed"], [100, 100, 101, 101, 102, 102])

        states = vec.states()
        np.testing.assert_allclose(states[:, 0], [0.0, 1.0, 2.0])
        np.testing.assert_allclose(states[:, 1], [0.0, 0.0, 0.0])

        vec.reset(seed=[11, 22, 33], options={"tag": "ok"})
        assert vec.get_attr("last_options") == [
            {"tag": "ok"},
            {"tag": "ok"},
            {"tag": "ok"},
        ]
        assert vec.get_attr("last_seed") == [11, 22, 33]

        with pytest.raises(ValueError, match="Expected 3 seeds"):
            vec.reset(seed=[1, 2])
    finally:
        vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_same_step_autoreset_preserves_final_obs_info_and_state(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    env_fns = [
        lambda: CounterStateParallelEnv(world_tag=10.0, horizon=2),
        lambda: CounterStateParallelEnv(
            world_tag=20.0, horizon=3, truncate_at_horizon=True
        ),
    ]
    vec = _make_runner(runner_cls, env_fns, autoreset_mode=AutoresetMode.SAME_STEP)
    try:
        vec.reset(seed=5)
        actions = np.array([1, 2, 0, 1], dtype=np.int64)

        obs1, rew1, term1, trunc1, info1 = vec.step(actions)
        assert not np.any(term1)
        assert not np.any(trunc1)
        np.testing.assert_allclose(rew1, [2.0, 4.0, 1.0, 3.0])
        np.testing.assert_allclose(obs1[:, 1], [1.0, 2.0, 1.0, 2.0])
        assert "final_obs" not in info1
        assert "final_state" not in info1

        # World 0 finishes at step 2 -> resets in place; terminal snapshot in infos.
        obs2, rew2, term2, trunc2, info2 = vec.step(actions)
        np.testing.assert_array_equal(term2, [True, True, False, False])
        np.testing.assert_array_equal(trunc2, [False, False, False, False])
        np.testing.assert_allclose(rew2, [2.0, 4.0, 1.0, 3.0])

        # Live World 0 arrays reflect the fresh reset (step 0), World 1 at step 2.
        np.testing.assert_allclose(obs2[:, 1], [0.0, 0.0, 2.0, 4.0])
        np.testing.assert_allclose(vec.states()[:, 1], [0.0, 2.0])

        # Terminal World 0 obs/info/state captured in final_* masks.
        np.testing.assert_array_equal(info2["_final_obs"], [True, True, False, False])
        np.testing.assert_allclose(
            info2["final_obs"][0], np.array([10.0, 2.0], dtype=np.float32)
        )
        np.testing.assert_allclose(
            info2["final_obs"][1], np.array([10.0, 4.0], dtype=np.float32)
        )
        assert info2["final_info"]["step"][0] == 2
        assert info2["final_info"]["world"][0] == 10
        np.testing.assert_array_equal(
            info2["final_info"]["_step"], [True, True, False, False]
        )
        np.testing.assert_array_equal(info2["_final_state"], [True, False])
        np.testing.assert_allclose(
            info2["final_state"][0], np.array([10.0, 2.0, 3.0], dtype=np.float32)
        )

        # Step 3: World 0 advances to 1 while World 1 truncates and autoresets.
        obs3, _, term3, trunc3, info3 = vec.step(actions)
        np.testing.assert_array_equal(term3, [False, False, False, False])
        np.testing.assert_array_equal(trunc3, [False, False, True, True])
        np.testing.assert_allclose(obs3[:, 1], [1.0, 2.0, 0.0, 0.0])
        np.testing.assert_array_equal(info3["_final_state"], [False, True])
        np.testing.assert_allclose(
            info3["final_state"][1], np.array([20.0, 3.0, 1.0], dtype=np.float32)
        )
    finally:
        vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_next_step_autoreset_resets_on_following_step(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    env_fns = [
        lambda: CounterStateParallelEnv(world_tag=1.0, horizon=2),
        lambda: CounterStateParallelEnv(world_tag=2.0, horizon=3),
    ]
    vec = _make_runner(runner_cls, env_fns, autoreset_mode="next_step")
    try:
        vec.reset(seed=0)
        actions = np.array([1, 1, 2, 0], dtype=np.int64)

        vec.step(actions)
        obs2, rew2, term2, _, info2 = vec.step(actions)
        np.testing.assert_array_equal(term2, [True, True, False, False])
        np.testing.assert_allclose(obs2[:, 1], [2.0, 4.0, 2.0, 4.0])
        assert "final_obs" not in info2
        assert "final_state" not in info2

        # Step 3 resets World 0 with zero rewards while World 1 terminates.
        obs3, rew3, term3, _, _ = vec.step(actions)
        np.testing.assert_array_equal(term3, [False, False, True, True])
        np.testing.assert_allclose(rew3[:2], [0.0, 0.0])
        np.testing.assert_allclose(obs3[:, 1], [0.0, 0.0, 3.0, 6.0])
        np.testing.assert_allclose(vec.states()[:, 1], [0.0, 3.0])
    finally:
        vec.close()


@pytest.mark.parametrize("mode", [AutoresetMode.SAME_STEP, AutoresetMode.NEXT_STEP])
def test_sync_and_async_exact_trajectory_parity(mode: AutoresetMode) -> None:
    def make_fns() -> list[Any]:
        return [
            lambda w=w: CounterStateParallelEnv(world_tag=w, horizon=2 + (w % 3))
            for w in range(5)
        ]

    sync_env = SyncParallelVectorEnv(make_fns(), autoreset_mode=mode)
    async_env = AsyncParallelVectorEnv(
        make_fns(), num_workers=2, autoreset_mode=mode, context="spawn"
    )
    try:
        s_obs, s_info = sync_env.reset(seed=42)
        a_obs, a_info = async_env.reset(seed=42)
        np.testing.assert_array_equal(s_obs, a_obs)
        np.testing.assert_array_equal(s_info["seed"], a_info["seed"])
        np.testing.assert_array_equal(sync_env.states(), async_env.states())

        rng = np.random.default_rng(7)
        for _ in range(7):
            actions = rng.integers(0, 3, size=sync_env.num_envs)
            so, sr, st, strunc, si = sync_env.step(actions)
            ao, ar, at, atrunc, ai = async_env.step(actions)

            np.testing.assert_array_equal(so, ao)
            np.testing.assert_array_equal(sr, ar)
            np.testing.assert_array_equal(st, at)
            np.testing.assert_array_equal(strunc, atrunc)
            np.testing.assert_array_equal(sync_env.states(), async_env.states())
            assert ("final_state" in si) == ("final_state" in ai)
            if "final_state" in si:
                np.testing.assert_array_equal(si["_final_state"], ai["_final_state"])
    finally:
        sync_env.close()
        async_env.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_call_get_attr_render_and_error_bounds(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    env_fns = [lambda w=w: CounterStateParallelEnv(world_tag=w) for w in range(3)]
    vec = _make_runner(runner_cls, env_fns)
    try:
        vec.reset(seed=1)
        vec.step(np.zeros(vec.num_envs, dtype=np.int64))

        assert vec.call("ping", 5) == [(0.0, 6), (1.0, 6), (2.0, 6)]
        assert vec.call("ping", offset=2, world_indices=[2, 0]) == [
            (2.0, 3),
            (0.0, 3),
        ]
        assert vec.get_attr("world_tag", world_indices=[1, 2]) == [1.0, 2.0]
        assert vec.render() == (
            "world=0,step=1",
            "world=1,step=1",
            "world=2,step=1",
        )

        with pytest.raises(TypeError, match="not callable"):
            vec.call("world_tag", 123)
        with pytest.raises(IndexError, match="out of range"):
            vec.get_attr("world_tag", world_indices=[3])
    finally:
        vec.close()


def test_async_step_async_step_wait_and_worker_clamping() -> None:
    env_fns = [lambda w=w: CounterStateParallelEnv(world_tag=w) for w in range(3)]
    vec = AsyncParallelVectorEnv(env_fns, num_workers=8, context="spawn")
    try:
        assert vec.num_workers == 3
        vec.reset(seed=9)

        with pytest.raises(RuntimeError, match="without a pending step_async"):
            vec.step_wait()

        vec.step_async(np.ones(vec.num_envs, dtype=np.int64))
        with pytest.raises(RuntimeError, match="awaiting step_wait"):
            vec.reset()
        with pytest.raises(RuntimeError, match="awaiting step_wait"):
            vec.call("ping")

        obs, rew, _, _, _ = vec.step_wait()
        np.testing.assert_allclose(obs[:, 1], [1.0, 2.0, 1.0, 2.0, 1.0, 2.0])
        np.testing.assert_allclose(rew, [2.0, 3.0, 2.0, 3.0, 2.0, 3.0])
    finally:
        vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_early_agent_departure_requires_black_death_wrapper(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    raw_vec = _make_runner(
        runner_cls, [EarlyDepartureParallelEnv, EarlyDepartureParallelEnv]
    )
    try:
        raw_vec.reset()
        with pytest.raises(ValueError, match="BlackDeathParallelV4"):
            raw_vec.step(np.zeros(raw_vec.num_envs, dtype=np.int64))
    finally:
        raw_vec.close()

    wrapped_vec = _make_runner(
        runner_cls,
        [
            lambda: BlackDeathParallelV4(EarlyDepartureParallelEnv()),
            lambda: BlackDeathParallelV4(EarlyDepartureParallelEnv()),
        ],
    )
    try:
        wrapped_vec.reset()
        _, rew1, term1, _, _ = wrapped_vec.step(
            np.zeros(wrapped_vec.num_envs, dtype=np.int64)
        )
        assert not np.any(term1)
        np.testing.assert_allclose(rew1, [-1.0, 1.0, -1.0, 1.0])

        obs2, rew2, term2, _, info2 = wrapped_vec.step(
            np.zeros(wrapped_vec.num_envs, dtype=np.int64)
        )
        assert np.all(term2)
        np.testing.assert_allclose(rew2, [0.0, 3.0, 0.0, 3.0])
        np.testing.assert_allclose(obs2, 0.0)
        assert np.all(info2["_final_obs"])
    finally:
        wrapped_vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_no_state_mismatch_validation_and_closed_errors(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    no_state = _make_runner(runner_cls, [NoStateParallelEnv, NoStateParallelEnv])
    try:
        assert not no_state.has_state
        assert no_state.state_space is None
        no_state.reset()
        no_state.step(np.zeros(no_state.num_envs, dtype=np.int64))
        with pytest.raises(NotImplementedError, match="state_space"):
            no_state.states()
    finally:
        no_state.close()
        no_state.close()

    with pytest.raises(ClosedEnvironmentError):
        no_state.reset()
    with pytest.raises(ClosedEnvironmentError):
        no_state.step(np.zeros(no_state.num_envs, dtype=np.int64))
    with pytest.raises(ClosedEnvironmentError):
        no_state.call("reset")

    with pytest.raises(ValueError, match="observation_space"):
        bad = _make_runner(
            runner_cls,
            [
                lambda: CounterStateParallelEnv(obs_dim=2),
                lambda: CounterStateParallelEnv(obs_dim=4),
            ],
        )
        bad.close()

    with pytest.raises(ValueError, match="possible_agents"):
        bad_agents = _make_runner(
            runner_cls,
            [
                lambda: CounterStateParallelEnv(num_agents=2),
                lambda: CounterStateParallelEnv(num_agents=3),
            ],
        )
        bad_agents.close()


class DictObsParallelEnv(ParallelEnv[str, dict[str, Any], int]):
    """Minimal ParallelEnv with Dict observation space for copy_tree tests."""

    metadata = {"name": "dict_obs_parallel_v0"}

    def __init__(self) -> None:
        self.possible_agents = ["a0", "a1"]
        self.agents: list[str] = []
        self.step_count = 0

    @functools.cache
    def observation_space(self, agent: str) -> Dict:
        return Dict(
            {
                "vec": Box(-10.0, 10.0, shape=(2,), dtype=np.float32),
                "flag": Discrete(2),
            }
        )

    @functools.cache
    def action_space(self, agent: str) -> Discrete:
        return Discrete(2)

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        self.agents = list(self.possible_agents)
        self.step_count = 0
        obs = {
            agent: {"vec": np.array([1.0, 2.0], dtype=np.float32), "flag": 1}
            for agent in self.agents
        }
        return obs, {agent: {} for agent in self.agents}

    def step(
        self, actions: dict[str, int]
    ) -> tuple[
        dict[str, dict[str, Any]],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        self.step_count += 1
        active = list(self.agents)
        obs = {
            agent: {
                "vec": np.array([float(self.step_count), 3.0], dtype=np.float32),
                "flag": actions[agent] % 2,
            }
            for agent in active
        }
        return (
            obs,
            dict.fromkeys(active, 0.0),
            dict.fromkeys(active, False),
            dict.fromkeys(active, False),
            {agent: {} for agent in active},
        )


def test_dict_observation_space_and_copy_semantics() -> None:
    copy_vec = SyncParallelVectorEnv(
        [DictObsParallelEnv, DictObsParallelEnv], copy=True
    )
    try:
        obs_c, _ = copy_vec.reset()
        obs_c["vec"][:] = -99.0
        np.testing.assert_allclose(
            copy_vec._observations["vec"], np.tile([1.0, 2.0], (4, 1))
        )
    finally:
        copy_vec.close()

    view_vec = SyncParallelVectorEnv(
        [DictObsParallelEnv, DictObsParallelEnv], copy=False
    )
    try:
        obs_v, _ = view_vec.reset()
        assert obs_v is view_vec._observations
        obs_v2, _, _, _, _ = view_vec.step(np.array([1, 0, 1, 0], dtype=np.int64))
        assert obs_v2 is view_vec._observations
        np.testing.assert_array_equal(obs_v2["flag"], [1, 0, 1, 0])
    finally:
        view_vec.close()


def test_constructor_and_worker_error_validation() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        SyncParallelVectorEnv([])
    with pytest.raises(ValueError, match="at least 1"):
        AsyncParallelVectorEnv([])
    with pytest.raises(ValueError, match="num_workers"):
        AsyncParallelVectorEnv([NoStateParallelEnv], num_workers=0)
    with pytest.raises(ValueError, match="autoreset_mode"):
        SyncParallelVectorEnv([NoStateParallelEnv], autoreset_mode="disabled")
    with pytest.raises(TypeError, match="ParallelEnv"):
        SyncParallelVectorEnv([lambda: "not_an_env"])  # type: ignore[list-item,return-value]
    with pytest.raises(TypeError, match="ParallelEnv"):
        AsyncParallelVectorEnv([lambda: "not_an_env"], context="spawn")  # type: ignore[list-item,return-value]

    async_vec = AsyncParallelVectorEnv(
        [CounterStateParallelEnv, CounterStateParallelEnv],
        num_workers=2,
        context="spawn",
    )
    try:
        async_vec.reset(seed=0)
        with pytest.raises(AttributeError):
            async_vec.call("nonexistent_method")
        assert async_vec.call("ping") == [(0.0, 0), (0.0, 0)]
    finally:
        async_vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_builtin_rps_v2_vector_rollout(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    from pettingzoo.classic.rps import rps

    env_fns = [lambda: rps.parallel_env(max_cycles=3) for _ in range(3)]
    vec = _make_runner(runner_cls, env_fns, num_workers=2)
    try:
        obs, _ = vec.reset(seed=7)
        assert obs.shape == (6,)
        assert vec.num_worlds == 3
        assert vec.agents_per_world == 2
        assert not vec.has_state

        for step_idx in range(4):
            actions = vec.action_space.sample()
            obs, rew, term, trunc, infos = vec.step(actions)
            assert vec.observation_space.contains(obs)
            assert rew.shape == (6,)
            if step_idx == 2:
                assert np.all(trunc)
                assert not np.any(term)
                assert np.all(infos["_final_obs"])
            else:
                assert not np.any(term)
                assert not np.any(trunc)
    finally:
        vec.close()


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_builtin_kaz_v11_black_death_and_states(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    pytest.importorskip("pygame")
    from pettingzoo.butterfly.knights_archers_zombies import knights_archers_zombies

    env_fns = [
        lambda: BlackDeathParallelV4(knights_archers_zombies.parallel_env(max_cycles=4))
        for _ in range(2)
    ]
    vec = _make_runner(runner_cls, env_fns, num_workers=2)
    try:
        obs, _ = vec.reset(seed=11)
        assert vec.num_worlds == 2
        assert vec.agents_per_world == 4
        assert vec.num_envs == 8
        assert vec.has_state
        assert vec.state_space is not None
        assert obs.shape == (8, *vec.single_observation_space.shape)
        assert vec.states().shape == (2, *vec.single_state_space.shape)

        for _ in range(5):
            actions = np.zeros(vec.num_envs, dtype=np.int64)
            obs, rew, term, trunc, _ = vec.step(actions)
            assert vec.observation_space.contains(obs)
            assert rew.shape == (8,)
            assert term.shape == (8,)
            assert trunc.shape == (8,)
            assert vec.states().shape == (2, *vec.single_state_space.shape)
    finally:
        vec.close()


class ReusingCounterParallelEnv(CounterStateParallelEnv):
    """Counter env reusing observation, state, and info buffers across resets."""

    def __init__(self) -> None:
        super().__init__(horizon=1)
        self.obs_buffers = {
            agent: np.zeros(2, dtype=np.float32) for agent in self.possible_agents
        }
        self.state_buffer = np.zeros(3, dtype=np.float32)
        self.info_buffers: dict[str, dict[str, Any]] = {
            agent: {} for agent in self.possible_agents
        }

    def _make_obs(self) -> dict[str, np.ndarray]:
        for agent, obs in super()._make_obs().items():
            self.obs_buffers[agent][:] = obs
        return {agent: self.obs_buffers[agent] for agent in self.agents}

    def state(self) -> np.ndarray:
        self.state_buffer[:] = super().state()
        return self.state_buffer

    def _reuse_info(
        self, infos: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        for agent, info in infos.items():
            self.info_buffers[agent].clear()
            self.info_buffers[agent].update(info)
        return {agent: self.info_buffers[agent] for agent in infos}

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, np.ndarray], dict[str, dict[str, Any]]]:
        obs, infos = super().reset(seed=seed, options=options)
        return obs, self._reuse_info(infos)

    def step(
        self, actions: dict[str, int]
    ) -> tuple[
        dict[str, np.ndarray],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        obs, rewards, terms, truncs, infos = super().step(actions)
        return obs, rewards, terms, truncs, self._reuse_info(infos)


@pytest.mark.parametrize("runner_cls", [SyncParallelVectorEnv, AsyncParallelVectorEnv])
def test_same_step_snapshots_reused_buffers(
    runner_cls: type[SyncParallelVectorEnv] | type[AsyncParallelVectorEnv],
) -> None:
    vec = _make_runner(runner_cls, [ReusingCounterParallelEnv])
    try:
        vec.reset()
        obs, _, terminated, _, infos = vec.step(np.array([1, 2], dtype=np.int64))
        assert terminated.all()
        np.testing.assert_array_equal(obs[:, 1], [0, 0])
        np.testing.assert_array_equal(infos["final_obs"][0], [0, 1])
        np.testing.assert_array_equal(infos["final_obs"][1], [0, 2])
        np.testing.assert_array_equal(infos["final_state"][0], [0, 1, 3])
        np.testing.assert_array_equal(infos["final_info"]["step"], [1, 1])
    finally:
        vec.close()
