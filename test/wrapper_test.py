from __future__ import annotations

import pytest

from pettingzoo.butterfly import pistonball_v6
from pettingzoo.classic import texas_holdem_no_limit_v6
from pettingzoo.utils.wrappers import MultiEpisodeEnv, MultiEpisodeParallelEnv


@pytest.mark.parametrize(("num_episodes"), [1, 2, 3, 4, 5, 6])
def test_multi_episode_env_wrapper(num_episodes: int) -> None:
    """test_multi_episode_env_wrapper.

    The number of steps per environment are dictated by the seeding of the action space, not the environment.

    Args:
        num_episodes: number of episodes to run the MultiEpisodeEnv
    """
    env = texas_holdem_no_limit_v6.env(num_players=3)
    env = MultiEpisodeEnv(env, num_episodes=num_episodes)
    env.reset(seed=42)

    steps = 0
    for agent in env.agent_iter():
        steps += 1
        obs, rew, term, trunc, info = env.last()

        if term or trunc:
            action = None
        else:
            action_space = env.action_space(agent)
            action_space.seed(0)
            action = action_space.sample(mask=obs["action_mask"])

        env.step(action)

    env.close()

    assert (
        steps == num_episodes * 6
    ), f"Expected to have 6 steps per episode, got {steps / num_episodes}."


@pytest.mark.parametrize(("num_episodes"), [1, 2, 3, 4, 5, 6])
def test_multi_episode_parallel_env_wrapper(num_episodes) -> None:
    """test_multi_episode_parallel_env_wrapper.

    The default action for this test is to move all pistons down. This results in an episode length of 125.

    Args:
        num_episodes: number of episodes to run the MultiEpisodeEnv
    """
    env = pistonball_v6.parallel_env()
    env = MultiEpisodeParallelEnv(env, num_episodes=num_episodes)
    _ = env.reset(seed=42)

    steps = 0
    while env.agents:
        steps += 1
        # this is where you would insert your policy
        actions = {agent: env.action_space(agent).low for agent in env.agents}

        _ = env.step(actions)

    env.close()

    assert (
        steps == num_episodes * 125
    ), f"Expected to have 125 steps per episode, got {steps / num_episodes}."
