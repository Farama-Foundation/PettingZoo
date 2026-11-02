import pytest

from pettingzoo import make


@pytest.mark.parametrize(
    "komi, expected_rewards",
    [
        (0, {"black_0": 0, "white_0": 0}),
        (7.5, {"black_0": -1, "white_0": 1}),
        (-7.5, {"black_0": 1, "white_0": -1}),
    ],
)
def test_rewards_after_both_players_pass(komi, expected_rewards):
    env = make("aec", "classic/go", board_size=5, komi=komi)
    try:
        env.reset(seed=0)
        env.step(25)
        env.step(25)
        assert all(env.terminations.values())
        assert env.rewards == expected_rewards
    finally:
        env.close()
