"""Serialization tests for the TicTacToe environment."""

from __future__ import annotations

import copy
import pickle

import numpy as np
import pytest

from pettingzoo.classic import tictactoe_v3


def _pickle_round_trip(env):
    return pickle.loads(pickle.dumps(env))


@pytest.mark.parametrize(
    "copy_env",
    [copy.deepcopy, _pickle_round_trip],
    ids=["deepcopy", "pickle"],
)
def test_copy_preserves_running_environment_state(copy_env) -> None:
    """Copying a running game preserves its state without sharing mutations."""
    env = tictactoe_v3.env(render_mode="rgb_array")
    env.reset(seed=7)
    env.step(0)
    env.step(4)

    copied_env = copy_env(env)

    assert copied_env.agent_selection == env.agent_selection
    assert copied_env.agents == env.agents
    assert copied_env.rewards == env.rewards
    assert copied_env._cumulative_rewards == env._cumulative_rewards
    assert copied_env.terminations == env.terminations
    assert copied_env.truncations == env.truncations
    assert copied_env.infos == env.infos
    assert copied_env.unwrapped.board.squares == env.unwrapped.board.squares

    copied_observation, *copied_last = copied_env.last()
    observation, *last = env.last()
    np.testing.assert_array_equal(
        copied_observation["observation"], observation["observation"]
    )
    np.testing.assert_array_equal(
        copied_observation["action_mask"], observation["action_mask"]
    )
    assert copied_last == last
    np.testing.assert_array_equal(copied_env.render(), env.render())

    copied_env.step(1)
    assert copied_env.unwrapped.board.squares == [1, 1, 0, 0, 2, 0, 0, 0, 0]
    assert env.unwrapped.board.squares == [1, 0, 0, 0, 2, 0, 0, 0, 0]

    copied_env.close()
    env.close()


@pytest.mark.parametrize(
    "copy_env",
    [copy.deepcopy, _pickle_round_trip],
    ids=["deepcopy", "pickle"],
)
def test_copy_preserves_terminal_rewards(copy_env) -> None:
    """Copying a finished game preserves rewards and termination state."""
    env = tictactoe_v3.env()
    env.reset(seed=7)
    for action in [0, 3, 1, 4, 2]:
        env.step(action)

    copied_env = copy_env(env)

    assert copied_env.unwrapped.board.squares == env.unwrapped.board.squares
    assert copied_env.rewards == {"player_1": 1, "player_2": -1}
    assert copied_env.rewards == env.rewards
    assert copied_env._cumulative_rewards == env._cumulative_rewards
    assert copied_env.terminations == {"player_1": True, "player_2": True}
    assert copied_env.terminations == env.terminations
    assert copied_env.last()[1:] == env.last()[1:]

    copied_env.close()
    env.close()
