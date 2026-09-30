import random
from copy import copy

import numpy as np

from pettingzoo.test.api_test import test_observation

try:
    import pytest

    from pettingzoo.test.example_envs import generated_agents_env_v0

    @pytest.fixture
    def env():
        env = generated_agents_env_v0.env()
        env.reset()
        return env

    @pytest.fixture
    def observation(env):
        return env.observation_space(env.agents[0]).sample()

    @pytest.fixture()
    def observation_0(env):
        return env.observation_space(env.agents[1]).sample()

    @pytest.fixture
    def cycles():
        return 1000

except ModuleNotFoundError:
    pass


def bombardment_test(env, cycles=10000):
    print("Starting bombardment test")

    env.reset()
    observation_0 = copy(env.last()[0])
    for i in range(cycles):
        if i == cycles / 2:
            print("\t50% through bombardment test")
        for agent in env.agent_iter(
            env.num_agents
        ):  # step through every agent once with observe=True
            obs, reward, termination, truncation, info = env.last()
            if termination or truncation:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                action = random.choice(np.flatnonzero(obs["action_mask"]).tolist())
            else:
                action = env.action_space(agent).sample()
            env.step(action)
            assert env.observation_space(agent).contains(obs), (
                "Agent's observation is outside of its observation space"
            )
            test_observation(obs, observation_0)
        env.reset()
    print("Passed bombardment test")
