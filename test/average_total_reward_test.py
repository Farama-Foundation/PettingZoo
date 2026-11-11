import io
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from pettingzoo import make
from pettingzoo.classic import connect_four_v3
from pettingzoo.utils.average_total_reward import average_total_reward
from pettingzoo.utils.env_logger import EnvLogger


def test_average_total_reward_does_not_sample_illegal_moves():
    EnvLogger.flush()
    env = connect_four_v3.env()
    with redirect_stdout(io.StringIO()):
        result = average_total_reward(env, max_episodes=20, max_steps=100000)
    assert isinstance(result, float)
    assert not any("Illegal move" in str(msg) for msg in EnvLogger.mqueue)


@pytest.mark.parametrize(
    ("max_steps", "expected_steps", "expected_episodes"),
    [(1, 1, 1), (4, 4, 1), (6, 6, 2), (12, 12, 3), (20, 12, 3)],
)
def test_average_total_reward_respects_step_budget(
    max_steps, expected_steps, expected_episodes
):
    # A one-cycle RPS episode takes two live steps and two dead-agent steps.
    env = make("aec", "classic/rps-v2", max_cycles=1)
    try:
        with (
            patch.object(env, "step", wraps=env.step) as step,
            patch.object(env, "reset", wraps=env.reset) as reset,
        ):
            average_total_reward(env, max_episodes=3, max_steps=max_steps)
            assert step.call_count == expected_steps
            assert reset.call_count == expected_episodes
    finally:
        env.close()
