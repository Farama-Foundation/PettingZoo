from __future__ import annotations

import pytest

from pettingzoo.butterfly import pistonball_v6
from pettingzoo.classic import texas_holdem_no_limit_v6, tictactoe_v3
from pettingzoo.utils.wrappers import (
    BaseWrapper,
    MultiEpisodeEnv,
    MultiEpisodeParallelEnv,
    TerminateIllegalWrapper,
)


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


def _do_game(env: TerminateIllegalWrapper, seed: int) -> None:
    """Run a single game with reproducible random moves."""
    assert isinstance(
        env, TerminateIllegalWrapper
    ), "test_terminate_illegal must use TerminateIllegalWrapper"
    env.reset(seed)
    for agent in env.agents:
        # make the random moves reproducible
        env.action_space(agent).seed(seed)

    for agent in env.agent_iter():
        _, _, termination, truncation, _ = env.last()

        if termination or truncation:
            env.step(None)
        else:
            action = env.action_space(agent).sample()
            env.step(action)


def test_terminate_illegal() -> None:
    """Test for a problem with terminate illegal wrapper.

    The problem is that env variables, including agent_selection, are set by
    calls from TerminateIllegalWrapper to env functions. However, they are
    called by the wrapper object, not the env so they are set in the wrapper
    object rather than the base env object. When the code later tries to run,
    the values get updated in the env code, but the wrapper pulls it's own
    values that shadow them.

    The test here confirms that is fixed.
    """
    # not using env() because we need to ensure that the env is
    # wrapped by TerminateIllegalWrapper
    raw_env = tictactoe_v3.raw_env()
    env = TerminateIllegalWrapper(raw_env, illegal_reward=-1)

    _do_game(env, 42)
    # bug is triggered by a corrupted state after a game is terminated
    # due to an illegal move. So we need to run the game twice to
    # see the effect.
    _do_game(env, 42)

    # get a list of what all the agent_selection values in the wrapper stack
    unwrapped = env
    agent_selections = []
    while unwrapped != env.unwrapped:
        # the actual value for this wrapper (or None if no value)
        agent_selections.append(unwrapped.__dict__.get("agent_selection", None))
        assert isinstance(unwrapped, BaseWrapper)
        unwrapped = unwrapped.env

    # last one from the actual env
    agent_selections.append(unwrapped.__dict__.get("agent_selection", None))

    # remove None from agent_selections
    agent_selections = [x for x in agent_selections if x is not None]

    # all values must be the same, or else the wrapper and env are mismatched
    assert len(set(agent_selections)) == 1, "agent_selection mismatch"
