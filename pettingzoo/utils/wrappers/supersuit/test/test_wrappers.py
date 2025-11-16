from pettingzoo.utils.wrappers.supersuit.basic_wrappers import color_reduction_v0, clip_reward_v0
import numpy as np
from gymnasium.spaces import Box, Discrete
from pettingzoo.utils.wrappers import OrderEnforcingWrapper as PettingzooWrap
from pettingzoo.utils.wrappers.supersuit.test.dummy_aec_env import DummyEnv
import pytest
from pettingzoo.utils.wrappers.supersuit.reward_lambda import reward_lambda_v0
from pettingzoo.utils.wrappers.supersuit.observation_lambda import observation_lambda_v0


def new_base_env():
    base_obs = {
        f"a{idx}": np.zeros([8, 8, 3], dtype=np.float32) + np.arange(3) + idx
        for idx in range(2)
    }
    base_obs_space = {
        f"a{idx}": Box(low=np.float32(0.0), high=np.float32(10.0), shape=[8, 8, 3])
        for idx in range(2)
    }
    base_act_spaces = {f"a{idx}": Discrete(5) for idx in range(2)}

    return DummyEnv(base_obs, base_obs_space, base_act_spaces)


def new_dummy():
    base_obs = {
        f"a_{idx}": (np.zeros([8, 8, 3], dtype=np.float32) + np.arange(3) + idx).astype(
            np.float32
        )
        for idx in range(2)
    }
    base_obs_space = {
        f"a_{idx}": Box(low=np.float32(0.0), high=np.float32(10.0), shape=[8, 8, 3])
        for idx in range(2)
    }
    base_act_spaces = {f"a_{idx}": Discrete(5) for idx in range(2)}

    return PettingzooWrap(DummyEnv(base_obs, base_obs_space, base_act_spaces))


wrappers = [
    color_reduction_v0(new_dummy(), "R"),
    clip_reward_v0(new_dummy()),
    reward_lambda_v0(new_dummy(), lambda x: x / 10),
]


@pytest.mark.parametrize("env", wrappers)
def test_basic_wrappers(env):
    env.reset(seed=5)
    obs, _, _, _, _ = env.last()
    act_space = env.action_space(env.agent_selection)
    obs_space = env.observation_space(env.agent_selection)
    first_obs = env.observe("a_0")
    assert obs_space.contains(first_obs)
    assert first_obs.dtype == obs_space.dtype
    env.step(act_space.sample())
    for agent in env.agent_iter():
        act_space = env.action_space(env.agent_selection)
        env.step(
            act_space.sample()
            if not (env.truncations[agent] or env.terminations[agent])
            else None
        )


def test_rew_lambda():
    env = reward_lambda_v0(new_dummy(), lambda x: x / 10)
    env.reset()
    assert env.rewards[env.agent_selection] == 1.0 / 10


def test_observation_lambda():
    def add1(obs, obs_space):
        return obs + 1

    base_env = new_base_env()
    env = observation_lambda_v0(base_env, add1)
    env.reset()
    obs0, _, _, _, _ = env.last()
    assert int(obs0[0][0][0]) == 1
    env = observation_lambda_v0(env, add1)
    env.reset()
    obs0, _, _, _, _ = env.last()
    assert int(obs0[0][0][0]) == 2

    def tile_obs(obs, obs_space):
        shape_size = len(obs.shape)
        tile_shape = [1] * shape_size
        tile_shape[0] *= 2
        return np.tile(obs, tile_shape)

    env = observation_lambda_v0(env, tile_obs)
    env.reset()
    obs0, _, _, _, _ = env.last()
    assert env.observation_space(env.agent_selection).shape == (16, 8, 3)

    def change_shape_fn(obs_space):
        return Box(low=0, high=1, shape=(32, 8, 3))

    env = observation_lambda_v0(env, tile_obs)
    env.reset()
    obs0, _, _, _, _ = env.last()
    assert env.observation_space(env.agent_selection).shape == (32, 8, 3)
    assert obs0.shape == (32, 8, 3)

    base_env = new_base_env()
    env = observation_lambda_v0(
        base_env,
        lambda obs, obs_space, agent: obs + base_env.possible_agents.index(agent),
    )
    env.reset()
    obs0 = env.observe(env.agents[0])
    obs1 = env.observe(env.agents[1])

    assert int(obs0[0][0][0]) == 0
    assert int(obs1[0][0][0]) == 2
    assert (
            env.observation_space(env.agents[0]).high + 1
            == env.observation_space(env.agents[1]).high
    ).all()

    base_env = new_base_env()
    env = observation_lambda_v0(
        base_env,
        lambda obs, obs_space, agent: obs + base_env.possible_agents.index(agent),
        lambda obs_space, agent: Box(
            obs_space.low, obs_space.high + base_env.possible_agents.index(agent)
        ),
    )
    env.reset()
    obs0 = env.observe(env.agents[0])
    obs1 = env.observe(env.agents[1])

    assert int(obs0[0][0][0]) == 0
    assert int(obs1[0][0][0]) == 2
    assert (
            env.observation_space(env.agents[0]).high + 1
            == env.observation_space(env.agents[1]).high
    ).all()
