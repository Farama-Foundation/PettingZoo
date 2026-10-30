"""Checks that the action masking tutorial's observations fit its declared observation space."""

import numpy as np
from gymnasium.spaces import Dict, MultiBinary, MultiDiscrete
from tutorial3_action_masking import CustomActionMaskedEnvironment


def test_observation_space_contains_observations():
    env = CustomActionMaskedEnvironment()

    for agent in env.possible_agents:
        space = env.observation_space(agent)
        assert isinstance(space, Dict)
        assert space["observation"] == MultiDiscrete([49, 49, 49])
        assert isinstance(space["action_mask"], MultiBinary)
        assert space["action_mask"].shape == (4,)
        assert space["action_mask"].dtype == np.int8

    observations, _ = env.reset(seed=42)
    for agent, obs in observations.items():
        assert obs in env.observation_space(agent), f"{agent} reset obs {obs}"

    for _ in range(100):
        if not env.agents:
            break
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, _, _, _, _ = env.step(actions)
        for agent, obs in observations.items():
            assert obs in env.observation_space(agent), f"{agent} step obs {obs}"


if __name__ == "__main__":
    test_observation_space_contains_observations()
    print("Observation space test passed.")
