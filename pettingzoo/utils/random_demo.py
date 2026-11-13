from __future__ import annotations

from typing import Any

import numpy as np

from pettingzoo.utils.env import AECEnv


def random_demo(
    env: AECEnv[Any, Any, Any], render: bool = True, episodes: int = 1
) -> float:
    """Runs an env object with random actions."""
    total_reward = 0
    completed_episodes = 0

    while completed_episodes < episodes:
        env.reset()
        for agent in env.agent_iter():
            if render:
                env.render()

            obs, reward, termination, truncation, info = env.last()
            total_reward += reward
            if termination or truncation:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                mask = np.asarray(obs["action_mask"], dtype=np.int8)
                action = env.action_space(agent).sample(mask=mask)
            elif isinstance(info, dict) and "action_mask" in info:
                mask = np.asarray(info["action_mask"], dtype=np.int8)
                action = env.action_space(agent).sample(mask=mask)
            else:
                action = env.action_space(agent).sample()
            env.step(action)

        completed_episodes += 1

    if render:
        env.close()

    print("Average total reward", total_reward / episodes)

    return total_reward
