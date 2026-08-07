"""Regression tests for env.agents cleanup when the environment is done.

See https://github.com/Farama-Foundation/PettingZoo/issues/1244

Terminated/truncated agents stay in ``env.agents`` until they take a final
vacuous ``step(None)``. Only after those steps is ``env.agents`` empty.
"""

from __future__ import annotations

import pytest

from pettingzoo.classic import connect_four_v3, rps_v2, tictactoe_v3


@pytest.mark.parametrize(
    "env_fn",
    [connect_four_v3.env, tictactoe_v3.env, rps_v2.env],
    ids=["connect_four", "tictactoe", "rps"],
)
def test_agents_empty_only_after_dead_steps(env_fn):
    """Agents remain listed when termination is first observed, then clear."""
    env = env_fn()
    env.reset(seed=42)

    saw_live_agent_terminated = False
    steps = 0
    max_steps = 500

    for agent in env.agent_iter():
        steps += 1
        assert steps <= max_steps, "episode did not finish"

        observation, reward, termination, truncation, info = env.last()
        done = termination or truncation

        if done:
            # Contract from the docs / issue #1244: agent is still present
            # when last() first reports termination/truncation.
            assert agent in env.agents, (
                "terminated agent must still be in env.agents before step(None)"
            )
            if len(env.agents) > 1 or not saw_live_agent_terminated:
                # At least once, termination is observed while agents remain.
                saw_live_agent_terminated = True
            action = None
        else:
            if isinstance(observation, dict) and "action_mask" in observation:
                action = env.action_space(agent).sample(observation["action_mask"])
            else:
                action = env.action_space(agent).sample()

        env.step(action)

        if done:
            # After the vacuous step, the agent that just acted is gone.
            assert agent not in env.agents, (
                "agent must be removed from env.agents after step(None)"
            )

    assert saw_live_agent_terminated, (
        "never observed a terminated agent still in agents"
    )
    assert not env.agents, "env.agents must be empty once the episode is fully done"
    assert env.num_agents == 0
    env.close()


def test_connect_four_user_mischeck_timing():
    """Reproduce the exact mistaken check from issue #1244.

    Checking ``not env.agents`` immediately when last() reports done is wrong;
    checking after the full agent_iter loop is correct.
    """
    env = connect_four_v3.env()
    env.reset(seed=42)

    mistaken_check_would_have_failed = False

    for agent in env.agent_iter():
        obs, _, termination, truncation, _ = env.last()

        if termination or truncation:
            if len(env.agents) > 0:
                mistaken_check_would_have_failed = True
            action = None
        else:
            mask = obs["action_mask"]
            action = env.action_space(agent).sample(mask)

        env.step(action)

    assert mistaken_check_would_have_failed, (
        "expected the premature not-env.agents check to fail mid-episode"
    )
    assert not env.agents
    env.close()
