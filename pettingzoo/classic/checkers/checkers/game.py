# Game logic for checkers

from __future__ import absolute_import, division, print_function
from six.moves import range


import itertools
import copy
import numpy as np


class Checkers:
    '''
    The board is represented by the positions of all pieces of different types belonging to the two players.
    The game state as the `board`, `turn`, `last_moved_piece`.
    A move is represented by the origin and destination squares by the current player.
    '''
    size = 8
    n_positions = int(size ** 2 // 2)
    n_per_row = int(size // 2)

    # TODO change players to top/bottom players
    all_players = ['black', 'white']
    all_piece_types = ['men', 'kings']

    # Converting to a flat representation of the board
    empty_square = 0
    black_man = 1
    black_king = 2
    white_man = 3
    white_king = 4

    # Directions
    pos2dir = ['sw', 'se', 'ne', 'nw']
    dir2del = [(+1, -1), (+1, +1), (-1, +1), (-1, -1)]

    # The directions a piece is allowed to move in
    legal_dirs = {
        'black': {
            'men': [0, 1],
            'kings': [0, 1, 2, 3],
        },
        'white': {
            'men': [2, 3],
            'kings': [0, 1, 2, 3],
        },
    }

    def __init__(self, board=None, turn='black', last_moved_piece=None, empty_corner=True):
        '''
        Args:
            empty_corner : bool
                If the upper left corner of the board should be used. Default to be False.
        '''
        # assert size == 8, 'Only supports size 8.'
        assert turn in Checkers.all_players, 'It must be either `black` or `white`\'s turn'
        self.empty_corner = empty_corner

        # Game state
        self._board = board or self.initial_board()
        self._turn = turn
        self._last_moved_piece = None

        # LUT for the neighboring 4 squares in each directions respectively. None for a missing neighbor
        # XXX there is another way to find neighbors (consider [sq+4, sq+5, sq-4, sq-5])
        self.neighbors = {sq: [] for sq in range(self.n_positions)}
        for sq in range(self.n_positions):
            row, col = self.sq2pos(sq)
            # For each direction
            for di, (drow, dcol) in enumerate(Checkers.dir2del):
                next_row, next_col = row + drow, col + dcol
                # Out of bound
                if not (0 <= next_row < self.size and 0 <= next_col < self.size):
                    self.neighbors[sq].append(None)
                else:
                    self.neighbors[sq].append(self.pos2sq(next_row, next_col))

    @staticmethod
    def initial_board():
        '''Returns the initial configuration of the board'''
        # Black starts at the top of the board
        board = {
            'black': {
                'men': set(range(12)),
                'kings': set(),
            },
            'white': {
                'men': set(range(32-12, 32)),
                'kings': set(),
            },
        }
        return board

    @staticmethod
    def empty_board():
        board = {
            'black': {
                'men': set(),
                'kings': set(),
            },
            'white': {
                'men': set(),
                'kings': set(),
            },
        }
        return board

    @staticmethod
    def immutable_board(board):
        # TODO Bitboard representation?
        pieces = (
            frozenset(board['black']['men']),
            frozenset(board['black']['kings']),
            frozenset(board['white']['men']),
            frozenset(board['white']['kings']),
        )
        return pieces

    @staticmethod
    def board_equal(board1, board2):
        return Checkers.immutable_board(board1) == Checkers.immutable_board(board2)

    @property
    def board(self):
        return self._board

    @property
    def turn(self):
        return self._turn

    @property
    def last_moved_piece(self):
        return self._last_moved_piece

    def move(self, from_sq, to_sq, skip_check=False):
        '''Update the game state after the current player moves its piece from `from_sq` to `to_sq`. Reference: https://en.wikipedia.org/wiki/English_draughts#Rules
        Args:
            skip_check : bool
                If the move is chosen from results returned by `legal_moves()`, the legality check can be skipped for efficiency. Default to be False.
        '''
        if not skip_check:
            # Reject illegal moves
            assert (from_sq, to_sq) in self.legal_moves(), 'The move is not legal.'

        # The move is legal
        switch_turn = True
        # Move the piece
        for type in ['men', 'kings']:
            pieces = self._board[self._turn][type]
            if from_sq in pieces:
                pieces.remove(from_sq)
                pieces.add(to_sq)
                piece_type = type
                self._last_moved_piece = to_sq
                break
        else:
            assert False, 'A friendly piece must be moved.'

        # The move is a jump
        if to_sq not in self.neighbors[from_sq]:
            # Remove the captured piece
            to_row, to_col = self.sq2pos(to_sq)
            from_row, from_col = self.sq2pos(from_sq)
            capture_row, capture_col = (from_row + to_row) / 2, (from_col + to_col) / 2
            capture_sq = self.pos2sq(capture_row, capture_col)
            for type in ['men', 'kings']:
                pieces = self._board[self.adversary][type]
                if capture_sq in pieces:
                    pieces.remove(capture_sq)
                    break
            else:
                assert False, 'An opposing piece must be captured.'
            # Check for new available jumps for the moved piece before crowning a king
            jumps = self.available_jumps(self._turn, piece_type, to_sq)
            # Switch the turn, if there is no more jumps for the current player
            switch_turn = len(jumps) == 0

        # Crowning a king (must end the turn)
        if piece_type == 'men':
            # Kings row is at the bottom for black
            if self._turn == 'black' and self.n_positions - to_sq <= self.n_per_row:
                self._board[self._turn]['men'].remove(to_sq)
                self._board[self._turn]['kings'].add(to_sq)
            # Kings row is at the top for white
            if self._turn == 'white' and to_sq < self.n_per_row:
                self._board[self._turn]['men'].remove(to_sq)
                self._board[self._turn]['kings'].add(to_sq)

        if switch_turn:
            self._turn = self.adversary
            self._last_moved_piece = None

        # Check win/loss, winner is None before the game ends
        all_next_moves = self.legal_moves()
        if len(all_next_moves) == 0:
            winner = self.adversary
        else:
            winner = None
        return self.board, self.turn, self.last_moved_piece, all_next_moves, winner

    @property
    def adversary(self):
        return 'black' if self._turn == 'white' else 'white'

    def available_simple_moves(self, player, type, sq):
        simple_moves = []
        for di in Checkers.legal_dirs[player][type]:
            next_sq = self.neighbors[sq][di]
            # There is a neighboring square
            if next_sq is not None:
                # Check its occupancy
                if not self.check_occupancy(next_sq):
                    simple_moves.append(next_sq)
        return simple_moves

    def check_occupancy(self, sq, by_players=all_players):
        '''
        Return : bool
            True if `sq` is occupied.
        '''
        for player in by_players:
            for type in ['men', 'kings']:
                if sq in self._board[player][type]:
                    return True
        return False

    def available_jumps(self, player, type, sq):
        '''Returns the available jumps of `player`'s piece of `type` at `sq`.'''
        jumps = []
        adversary = 'black' if player == 'white' else 'white'
        for di in Checkers.legal_dirs[player][type]:
            capture_sq = self.neighbors[sq][di]
            # There is a neighboring square
            if capture_sq is not None:
                # The square is occupied by the adversary's piece
                if self.check_occupancy(capture_sq, [adversary]):
                    # Must jump over two squares in a single direction
                    next_sq = self.neighbors[capture_sq][di]
                    if next_sq is not None:
                        # The square is not occupied
                        if not self.check_occupancy(next_sq):
                            jumps.append(next_sq)
        return jumps

    def all_jumps(self):
        if self._last_moved_piece is None:
            jumps = []
            for type in ['men', 'kings']:
                for sq in self._board[self._turn][type]:
                    jumps += itertools.product([sq], self.available_jumps(self._turn, type, sq))
        else:
            piece_type = 'men' if self._last_moved_piece in self._board[self._turn]['men'] else 'kings'
            jumps = itertools.product([self._last_moved_piece], self.available_jumps(self._turn, piece_type, self._last_moved_piece))
        return list(jumps)

    def legal_moves(self):
        '''Returns all legal moves of the current `player`.'''
        all_moves = self.all_jumps()
        # Jumps are mandatory
        if 0 < len(all_moves):
            return all_moves
        # No jumps available
        for type in ['men', 'kings']:
            for sq in self._board[self._turn][type]:
                all_moves += itertools.product([sq], self.available_simple_moves(self._turn, type, sq))
        return all_moves

    def pos2sq(self, row, col):
        if self.empty_corner and row % 2 == 0:
            # Even rows starts with an empty square
            col -= 1
        elif not self.empty_corner and row % 2 == 1:
            # Odd rows starts with an empty square
            col -= 1
        col /= 2
        return int(row * (self.size / 2) + col)

    def sq2pos(self, sq):
        row, col = int(sq // (self.size / 2)), int(sq % (self.size / 2))
        col *= 2
        if self.empty_corner and row % 2 == 0:
            # Even rows starts with an empty square
            col += 1
        elif not self.empty_corner and row % 2 == 1:
            # Odd rows starts with an empty square
            col += 1
        return row, col

    def flat_board(self):
        # Empty board
        board = np.ones((self.size, self.size), dtype='int') * Checkers.empty_square
        # Place the pieces
        for sq in self._board['black']['men']:
            row, col = self.sq2pos(sq)
            board[row][col] = Checkers.black_man
        for sq in self._board['black']['kings']:
            row, col = self.sq2pos(sq)
            board[row][col] = Checkers.black_king
        for sq in self._board['white']['men']:
            row, col = self.sq2pos(sq)
            board[row][col] = Checkers.white_man
        for sq in self._board['white']['kings']:
            row, col = self.sq2pos(sq)
            board[row][col] = Checkers.white_king
        return board

    def print_board(self):
        # Symbols
        empty_square = '_'
        empty_playable_square = '.'
        black_man = 'b'
        black_king = 'B'
        white_man = 'w'
        white_king = 'W'
        symbols = [empty_playable_square, black_man, black_king, white_man, white_king]
        # Print board
        for i, row in enumerate(self.flat_board()):
            for j, col in enumerate(row):
                if ((i + self.empty_corner) % 2 + j) % 2 == 1:
                    # Not playable squares
                    print(empty_square, end='')
                else:
                    print(symbols[col], end='')
            print()

    def print_empty_board(self):
        '''Display the standard representation of the board with squares:
        __00__01__02__03
        04__05__06__07__
        __08__09__10__11
        12__13__14__15__
        __16__17__18__19
        20__21__22__23__
        __24__25__26__27
        28__29__30__31__
        '''
        board = -1 * np.ones((self.size, self.size), dtype='int')
        # Print board
        for sq in range(self.n_positions):
            board[self.sq2pos(sq)] = sq
        for row in board:
            for col in row:
                print('__' if col < 0 else '%02i' % col, end='')
            print()

    def save_state(self):
        return copy.deepcopy(self.board), self.turn, self.last_moved_piece

    def restore_state(self, state):
        board, turn, last_moved_piece = state
        self._board = copy.deepcopy(board)
        self._turn = turn
        self._last_moved_piece = last_moved_piece


if __name__ == '__main__':
    ch = Checkers(empty_corner=True)
    ch.print_empty_board()
    state = ch.save_state()
    assert ch.sq2pos(31) == (7, 6)
    assert ch.pos2sq(7, 6) == 31
    print(ch.flat_board())
    ch._board['white']['kings'].add(13)
    ch.print_board()
    print(ch.neighbors)
    print(ch.available_simple_moves('black', 'men', 8))
    print(ch.available_jumps('black', 'men', 8))
    print(ch.legal_moves())
    print(ch.move(8, 17))
    ch.print_board()
    ch.restore_state(state)

    # Play a quick game
    ply = 0
    winner = None
    while winner is None:
        # Select a legal move for the current player
        move = ch.legal_moves()[0]
        board, turn, last_moved_piece, moves, winner = ch.move(*move, skip_check=True)
        ch.print_board()
        print(ply, turn, last_moved_piece, winner)
        ply += 1
