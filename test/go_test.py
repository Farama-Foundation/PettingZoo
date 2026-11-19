import numpy as np
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


def play_randomly(env, seed, num_moves):
    """Plays random legal moves and then passes twice, yielding after every step."""
    rng = np.random.default_rng(seed)
    env.reset(seed=seed)
    for i in range(num_moves + 2):
        observation, _, termination, truncation, _ = env.last()
        if termination or truncation:
            break
        action_mask = observation["action_mask"]
        if i < num_moves:
            action = rng.choice(np.flatnonzero(action_mask))
        else:
            action = len(action_mask) - 1  # pass
        env.step(action)
        yield observation["observation"], action_mask
    yield env.rewards, env.render()


def test_different_board_sizes_side_by_side():
    """Environments with different board sizes don't affect each other."""
    sizes = [9, 19, 5]
    expected = []
    for size in sizes:
        env = make("aec", "classic/go", board_size=size, render_mode="rgb_array")
        expected.append(list(play_randomly(env, seed=size, num_moves=40)))
        env.close()

    # Create all environments before resetting any, then step them in turns
    envs = [
        make("aec", "classic/go", board_size=size, render_mode="rgb_array")
        for size in sizes
    ]
    games = [
        play_randomly(env, seed=size, num_moves=40) for env, size in zip(envs, sizes)
    ]
    rounds = list(zip(*games))  # each round steps every environment once
    outputs = list(zip(*rounds))
    for env in envs:
        env.close()

    for output, expected_output in zip(outputs, expected):
        assert len(output) == len(expected_output)
        for step, expected_step in zip(output, expected_output):
            for value, expected_value in zip(step, expected_step):
                np.testing.assert_equal(value, expected_value)
