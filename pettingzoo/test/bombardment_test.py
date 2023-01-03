import random
from copy import copy

import numpy as np

from .api_test import test_observation


def bombardment_test(env, cycles=10000):
    print("Starting bombardment test")

    env.reset()
    prev_observe, *_ = env.last()
    observation_0 = copy(prev_observe)
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
                action = random.choice(np.flatnonzero(obs["action_mask"]))
            else:
                action = env.action_space(agent).sample()
            next_observe = env.step(action)
            assert env.observation_space(agent).contains(
                prev_observe
            ), "Agent's observation is outside of its observation space"
            test_observation(prev_observe, observation_0)
            prev_observe = next_observe
        env.reset()
        prev_observe, *_ = env.last()
    print("Passed bombardment test")
