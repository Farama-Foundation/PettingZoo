from __future__ import annotations

import random

import numpy as np

from pettingzoo.utils.env import AECEnv


def average_total_reward(
    env: AECEnv, max_episodes: int = 100, max_steps: int = 10000000000
) -> float:
    """Calculates the average total reward over the episodes for AEC environments.

    Runs an env object with random actions until either max_episodes or
    max_steps is reached.
    Reward is summed across all agents, making it unsuited for use in zero-sum
    games.
    """
    total_reward = 0
    total_steps = 0
    num_episodes = 0

    for episode in range(max_episodes):
        if total_steps >= max_steps:
            break

        env.reset()
        for agent in env.agent_iter():
            # Because we call env.last() this function only works with AEC envs
            obs, reward, termination, truncation, _ = env.last(observe=False)
            total_reward += reward
            total_steps += 1
            if termination or truncation:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                action = random.choice(np.flatnonzero(obs["action_mask"]).tolist())
            else:
                action = env.action_space(agent).sample()
            env.step(action)

        num_episodes = episode + 1
    print("Average total reward", total_reward / num_episodes)

    return total_reward / num_episodes
