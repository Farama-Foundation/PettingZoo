from checkers.game import Checkers

def test_multi_jump():
    '''Handling a multi-jump'''
    # _._b_._.
    # ._w_._._
    # _._._._.
    # ._w_._._
    # _._._._.
    # ._w_._._
    # _._._._.
    # ._._._._
    board = Checkers.empty_board()
    board['black']['men'].add(1)
    board['white']['men'].update([5, 5 + 4 * 2, 5 + 4 * 4])
    ch = Checkers(board=board)
    assert len(ch.legal_moves()) == 1, 'Should only have one legal move.'
    assert ch.legal_moves()[0] == (1, 8), 'The only legal move should be (1, 8).'
    ch.move(1, 8)
    assert ch.turn == 'black', 'Black still have more jumps so it is Black\'s turn.'

def test_single_piece_moved():
    '''Only one piece is allowed to move within one s turn'''
    # _b_._._.
    # ._w_b_._
    # _._._w_.
    # ._._w_._
    # _._._._.
    # ._._._._
    # _._._._.
    # ._._._._
    board = Checkers.empty_board()
    board['black']['men'].update([0, 6])
    board['white']['men'].update([5, 5 + 5, 14])
    ch = Checkers(board=board)
    state = ch.save_state()
    ch.move(0, 9)
    assert ch.turn == 'black' and ch.last_moved_piece == 9, 'Black still have more jumps.'
    ch.restore_state(state)
    ch.move(6, 15)
    assert ch.turn == 'white', 'Black finished its turn.'
