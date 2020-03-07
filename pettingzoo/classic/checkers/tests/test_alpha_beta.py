from checkers.game import Checkers
from checkers.agents.alpha_beta import MinimaxPlayer

def test_opposing_duo():
    '''A sanity test for a look-ahead agent'''
    # _._._._.
    # ._._._._
    # _._._._.
    # ._._._b_
    # _._._._.
    # ._._._w_
    # _._._._.
    # ._._._._
    board = Checkers.empty_board()
    board['black']['men'].add(15)
    board['white']['men'].add(23)
    ch = Checkers(board=board, turn='black')
    black_player = MinimaxPlayer('black', search_depth=2)
    from_sq, to_sq = black_player.next_move(ch.board, ch.last_moved_piece)
    assert to_sq == 19, 'Should move to the edge for safety.'
