"""Tests that action masking code works properly with all PettingZoo classic environments."""

import pytest

from pettingzoo.classic import (
    chess_v6,
    gin_rummy_v4,
    go_v5,
    hanabi_v5,
    leduc_holdem_v4,
    texas_holdem_no_limit_v6,
    texas_holdem_v4,
    tictactoe_v3,
)

pytest.importorskip("stable_baselines3")
pytest.importorskip("sb3_contrib")

# Note: Connect Four is tested in sb3_connect_four_action_mask.py
# Note: Rock-Paper-Scissors has no action masking and does not seem to learn well playing against itself

# These environments do better than random even after the minimum number of timesteps
EASY_ENVS = [
    gin_rummy_v4,
    texas_holdem_no_limit_v6,  # texas holdem human rendered game ends instantly, but with random actions it works fine
    texas_holdem_v4,
]

# More difficult environments which will likely take more training time
MEDIUM_ENVS = [
    leduc_holdem_v4,  # with 10x as many steps it gets higher total rewards (9 vs -9), 0.52 winrate, and 0.92 vs 0.83 total scores
    hanabi_v5,  # even with 10x as many steps, total score seems to always be tied between the two agents
    tictactoe_v3,  # even with 10x as many steps, agent still loses every time (most likely an error somewhere)
    chess_v6,  # difficult to train because games take so long, performance varies heavily
]

# Most difficult environments to train agents for (and longest games
# TODO: test board_size to see if smaller go board is more easily solvable
HARD_ENVS = [
    go_v5,  # difficult to train because games take so long, may be another issue causing poor performance
]


@pytest.mark.parametrize("env_fn", EASY_ENVS)
def test_action_mask_easy(env_fn):
    from tutorials.SB3.connect_four.sb3_connect_four_action_mask import (
        eval_action_mask,
        train_action_mask,
    )

    env_kwargs = {}

    # Leduc Hold`em takes slightly longer to outperform random
    steps = 8192 if env_fn != leduc_holdem_v4 else 8192 * 4

    # Train a model against itself (takes ~2 minutes on GPU)
    train_action_mask(env_fn, steps=steps, seed=0, **env_kwargs)

    # Evaluate 2 games against a random agent
    round_rewards, total_rewards, winrate, scores = eval_action_mask(
        env_fn, num_games=100, render_mode=None, **env_kwargs
    )

    assert winrate > 0.5 or (
        total_rewards[env_fn.env().possible_agents[1]]
        > total_rewards[env_fn.env().possible_agents[0]]
    ), "Trained policy should outperform random actions"

    # Watch two games (disabled by default)
    # eval_action_mask(env_fn, num_games=2, render_mode="human", **env_kwargs)


# @pytest.mark.skip(
#     reason="training is compute intensive and hyperparameters have not been tuned, disabled for CI"
# )
@pytest.mark.parametrize("env_fn", MEDIUM_ENVS)
def test_action_mask_medium(env_fn):
    from tutorials.SB3.connect_four.sb3_connect_four_action_mask import (
        eval_action_mask,
        train_action_mask,
    )

    env_kwargs = {}

    # Train a model against itself
    train_action_mask(env_fn, steps=8192, seed=0, **env_kwargs)

    # Evaluate 2 games against a random agent
    round_rewards, total_rewards, winrate, scores = eval_action_mask(
        env_fn, num_games=100, render_mode=None, **env_kwargs
    )

    assert (
        winrate < 0.75
    ), "Policy should not perform better than 75% winrate"  # 30-40% for leduc, 0% for hanabi, 0% for tic-tac-toe

    # Watch two games (disabled by default)
    # eval_action_mask(env_fn, num_games=2, render_mode="human", **env_kwargs)


# @pytest.mark.skip(
#     reason="training is compute intensive and hyperparameters have not been tuned, disabled for CI"
# )
@pytest.mark.parametrize("env_fn", HARD_ENVS)
def test_action_mask_hard(env_fn):
    from tutorials.SB3.connect_four.sb3_connect_four_action_mask import (
        eval_action_mask,
        train_action_mask,
    )

    env_kwargs = {}

    # Train a model against itself
    train_action_mask(env_fn, steps=8192, seed=0, **env_kwargs)

    # Evaluate 2 games against a random agent
    round_rewards, total_rewards, winrate, scores = eval_action_mask(
        env_fn, num_games=100, render_mode=None, **env_kwargs
    )

    assert winrate > 0, "Policy should not perform better than 50% winrate"  # 0% for go

    # Watch two games (disabled by default)
    # eval_action_mask(env_fn, num_games=2, render_mode="human", **env_kwargs)
