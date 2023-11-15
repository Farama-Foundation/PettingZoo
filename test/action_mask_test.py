from typing import Type

import pytest

from pettingzoo.test import api_test, seed_test
from pettingzoo.test.example_envs import (
    generated_agents_env_action_mask_info_v0,
    generated_agents_env_action_mask_obs_v0,
)
from pettingzoo.utils.env import AECEnv


@pytest.mark.parametrize(
    "env_constructor",
    [
        generated_agents_env_action_mask_info_v0.env,
        generated_agents_env_action_mask_obs_v0.env,
    ],
)
def test_action_mask(env_constructor: Type[AECEnv]):
    """Test that environments function deterministically in cases where action mask is in observation, or in info."""
    seed_test(env_constructor)
    api_test(env_constructor())

    # Step through the environment according to example code given in AEC documentation (following action mask)
    env = env_constructor()
    env.reset(seed=42)
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        else:
            # invalid action masking is optional and environment-dependent
            if "action_mask" in info:
                mask = info["action_mask"]
            elif isinstance(observation, dict) and "action_mask" in observation:
                mask = observation["action_mask"]
            else:
                mask = None
            action = env.action_space(agent).sample(mask)
        env.step(action)
    env.close()
