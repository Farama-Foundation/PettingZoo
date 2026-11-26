import chess
import numpy as np
import pytest

from pettingzoo.classic.chess import chess_utils
from pettingzoo.classic.chess.chess import raw_env


def assert_asserts(x):
    try:
        x()
    except AssertionError:
        return True
    return False


def test_chess():
    assert chess_utils.move_to_coord(chess.Move.from_uci("a8b7")) == (0, 7)
    assert chess_utils.move_to_coord(chess.Move.from_uci("g3b7")) == (6, 2)

    assert chess_utils.get_knight_dir((2, 1)) == 7
    assert chess_utils.get_knight_dir((-2, 1)) == 1
    assert assert_asserts(lambda: chess_utils.get_knight_dir((-1, 1)))

    assert chess_utils.get_queen_dir((5, -5)) == (4, 5)
    assert chess_utils.get_queen_dir((8, 0)) == (7, 6)
    assert chess_utils.get_queen_dir((0, -1)) == (0, 3)
    assert assert_asserts(lambda: chess_utils.get_queen_dir((0, 0)))
    assert assert_asserts(lambda: chess_utils.get_queen_dir((1, 2)))
    assert assert_asserts(lambda: chess_utils.get_queen_dir((2, -8)))

    assert chess_utils.get_move_plane(
        chess.Move.from_uci("e1g1")
    ) == chess_utils.get_queen_plane((2, 0))  # castles kingside
    assert chess_utils.get_move_plane(
        chess.Move.from_uci("g1f3")
    ) == 56 + chess_utils.get_knight_dir((-1, 2))  # castles kingside
    assert chess_utils.get_move_plane(
        chess.Move.from_uci("f7f8q")
    ) == chess_utils.get_queen_plane((0, 1))
    assert (
        chess_utils.get_move_plane(chess.Move.from_uci("f7f8r")) == 56 + 8 + 2 + 1 * 3
    )
    assert (
        chess_utils.get_move_plane(chess.Move.from_uci("f7g8n")) == 56 + 8 + 0 + 2 * 3
    )

    assert str(chess_utils.mirror_move(chess.Move.from_uci("f7g8"))) == "f2g1"

    board = chess.Board()
    board.push_san("e4")
    test_action = np.ones([8, 8, 73]) * -100
    test_action[0, 1, 4] = 1
    board.push_san("c5")
    _ = chess_utils.get_observation(board, player=1)
    board.push_san("e5")
    _ = chess_utils.get_observation(board, player=1)
    board.push_san("d5")
    _ = chess_utils.get_observation(board, player=1)
    board.push_san("a3")
    _ = chess_utils.get_observation(board, player=1)
    board.push_san("d4")
    _ = chess_utils.get_observation(board, player=1)
    board.push_san("c4")
    _ = chess_utils.get_observation(board, player=1)


def step_uci(env, uci_move):
    """Steps the action that plays `uci_move` on the board."""
    player = env.possible_agents.index(env.agent_selection)
    action_mask = env.observe(env.agent_selection)["action_mask"]
    for action in np.flatnonzero(action_mask):
        if chess_utils.action_to_move(env.board, action, player).uci() == uci_move:
            env.step(action)
            return
    raise AssertionError(f"{uci_move} is not legal")


def board_channels(board, player):
    """The 13 channels that represent `board` in the observation of `player`."""
    channels = chess_utils.get_observation(board, player)[:, :, 7:20].copy()
    channels[:, :, 12] = board.is_repetition(2)
    return channels


def test_observation_board_history():
    """Channels 7 - 110 hold the current board and the 7 boards before it."""
    # After 4 plies the start position repeats. After 8 plies it is no longer
    # one of the 8 boards in the observation.
    moves = [
        "g1f3",
        "g8f6",
        "f3g1",
        "f6g8",
        "e2e4",
        "c7c5",
        "g1f3",
        "d7d6",
        "d2d4",
        "c5d4",
    ]
    env = raw_env()
    env.reset()
    for ply in range(len(moves) + 1):
        if ply > 0:
            step_uci(env, moves[ply - 1])
        for player, agent in enumerate(env.possible_agents):
            observation = env.observe(agent)["observation"]
            board = env.board.copy()
            for i in range(8):
                channels = observation[:, :, 7 + 13 * i : 20 + 13 * i]
                if i <= ply:
                    assert (channels == board_channels(board, player)).all()
                    if i < ply:
                        board.pop()
                else:
                    assert not channels.any()
    # The repetition after 4 plies is 6 boards back after 10 plies
    assert observation[:, :, 7 + 13 * 6 + 12].all()


@pytest.mark.parametrize(
    "fen, castling",
    [
        # White can only castle kingside, black only queenside
        ("r3k2r/8/8/8/8/8/8/R3K2R w Kq - 0 1", [[0, 1, 1, 0], [1, 0, 0, 1]]),
        ("r3k2r/8/8/8/8/8/8/R3K2R b Kq - 0 1", [[0, 1, 1, 0], [1, 0, 0, 1]]),
        # White can only castle queenside, black only kingside
        ("r3k2r/8/8/8/8/8/8/R3K2R w Qk - 0 1", [[1, 0, 0, 1], [0, 1, 1, 0]]),
    ],
)
def test_observation_castling_channels(fen, castling):
    """Channels 0 - 3: own queenside, own kingside, opponent queenside and kingside."""
    env = raw_env()
    env.reset()
    env.board = chess.Board(fen)
    for player, agent in enumerate(env.possible_agents):
        observation = env.observe(agent)["observation"]
        for channel, expected in enumerate(castling[player]):
            assert (observation[:, :, channel] == expected).all()


@pytest.mark.parametrize("halfmove_clock", [0, 1, 6, 13, 99])
@pytest.mark.parametrize("turn", ["w", "b"])
def test_observation_move_clock_channel(halfmove_clock, turn):
    """The n-th element of flattened channel 5 is set after n moves, for both players."""
    env = raw_env()
    env.reset()
    env.board = chess.Board(f"4k3/8/8/8/8/8/8/R3K3 {turn} - - {halfmove_clock} 60")
    for agent in env.possible_agents:
        move_clock = env.observe(agent)["observation"][:, :, 5].flatten()
        assert np.flatnonzero(move_clock).tolist() == [halfmove_clock // 2]
