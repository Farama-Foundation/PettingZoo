"""Test file to ensure that action masking code works for all PettingZoo classic environments (except rps, which has no action mask)."""

try:
    import pytest
    from tutorials.SB3.render_sb3_chess_action_mask import watch_action_mask
    from tutorials.SB3.sb3_chess_action_mask import train_action_mask
except ModuleNotFoundError:
    pass

from pettingzoo.classic import (
    chess_v6,
    connect_four_v3,
    gin_rummy_v4,
    hanabi_v4,
    leduc_holdem_v4,
    texas_holdem_no_limit_v6,
    texas_holdem_v4,
    tictactoe_v3,
)

WORKING_ENVS = [
    tictactoe_v3,
    connect_four_v3,
    chess_v6,
    leduc_holdem_v4,
    gin_rummy_v4,
    hanabi_v4,
    # texas holdem likely broken, game ends instantly, but with random actions it works fine
    texas_holdem_no_limit_v6,
    texas_holdem_v4,
]


@pytest.mark.parametrize("env_fn", WORKING_ENVS)
def test_action_mask(env_fn):
    train_action_mask(env_fn, steps=2048)
    watch_action_mask(env_fn)
