# Minimax with alpha-beta pruning and a hand-crafted valuation function
from __future__ import absolute_import, division, print_function
from six.moves import range


import time
from functools import partial
from collections import defaultdict

import numpy as np

from checkers.game import Checkers
from checkers.agents import Player


class MinimaxPlayer(Player):
    '''Minimax search with alpha-beta pruning'''
    # TODO killer move heuristic
    # TODO history heuristic
    # The value of all the outcomes
    win, draw, loss = float('inf'), 0, float('-inf')

    def __init__(self, color, value_func=None, search_depth=float('inf'), rollout_order_gen=None, seed=None):
        super(MinimaxPlayer, self).__init__(color=color, seed=seed)

        # Search depth = 0 is a random player
        assert 0 < search_depth, '`search_depth` must be greater than 0.'

        self.adversary = 'black' if self.color == 'white' else 'white'
        # Default to evaluate using material value heuristic
        self.value = value_func or partial(material_value_adv, self.color, 2, 1)
        # Default to evaluate actions at a random order
        self.rollout_order = rollout_order_gen or (lambda moves: self.random.permutation(np.asarray(moves, dtype='int,int')))
        # Cache the evaluated values
        # TODO transposition table
        # TODO add endgame database
        self.cached_values = {}
        self.search_depth = search_depth
        self.ply = 0

        # Statistics
        self.n_evaluated_positions = 0
        self.evaluation_dt = 0
        self.prunes = defaultdict(lambda: 0)

    @staticmethod
    def immutable_state(board, turn, last_moved_piece):
        return Checkers.immutable_board(board), turn, last_moved_piece

    def add_to_cache(self, immutable_state, value):
        # TODO evict some cache to prevent over-capacity
        self.cached_values[immutable_state] = value

    def next_move(self, board, last_moved_piece):
        state = board, self.color, last_moved_piece
        t0 = time.time()
        m0 = self.n_evaluated_positions
        self.simulator.restore_state(state)
        moves = self.simulator.legal_moves()
        if len(moves) == 1:
            # No other choice
            best_move = moves[0]
        else:
            # More than one legal move
            value, best_move = self.minimax_search(state, MinimaxPlayer.loss, MinimaxPlayer.win, self.search_depth, set())
            # print('move', move, 'value', value)
        dt = time.time() - t0
        dm = self.n_evaluated_positions - m0
        print('evaluated %i positions in %.2fs (avg %.2f positions/s) with effective branching factor %.2f' % (dm, dt, dm / dt, dm ** (1 / self.search_depth)))
        self.evaluation_dt += dt
        self.ply += 1
        return best_move

    def minimax_search(self, state, alpha, beta, depth, visited_states):
        '''
        Bounded depth first minimax search with alpha-beta pruning.
        Suppose that we can evaluate k positions per second, then in m seconds, with an effective branching factor b~5, we can search a depth of ~[log(m) + log(k)] / log(b).
        '''
        # XXX visited_states should only track a path?
        # print(depth, alpha, beta)
        board, turn, last_moved_piece = state
        im_state = MinimaxPlayer.immutable_state(*state)

        # Already evaluated?
        if im_state in self.cached_values:
            # print('cache hit')
            self.cached_values[im_state]

        # Evaluate this state
        self.simulator.restore_state(state)
        moves = self.simulator.legal_moves()
        # Base case. Win/loss check
        if len(moves) == 0:
            # No available moves => loss
            value = MinimaxPlayer.loss if turn == self.color else MinimaxPlayer.win
            self.add_to_cache(im_state, value)
            # print(self.color == turn, depth, 'end', value, 'no more moves')
            self.n_evaluated_positions += 1
            return value, None

        # Order moves based on ordering heuristic
        ordered_moves = self.rollout_order(moves)
        # We should terminate the rollout early
        if depth == 0:
            # Terminate with a valuation function
            value = self.value(*state)
            # print(self.color == turn, depth, 'end', value)
            self.n_evaluated_positions += 1
            return value, ordered_moves[0]
        # Rollout each legal move
        best_move = ordered_moves[0]
        if turn == self.color:
            # Maximizing node
            extreme_value = alpha
            for move in ordered_moves:
                # print(self.color == turn, depth, move, state[0])
                self.simulator.restore_state(state)
                next_board, next_turn, next_last_moved_piece, next_moves, winner = self.simulator.move(*move, skip_check=True)
                # print(self.color == turn, depth, move, next_board)
                next_state = self.simulator.save_state()
                # Evaluate the next position
                value, _ = self.minimax_search(next_state, extreme_value, beta, depth=depth-1, visited_states=visited_states)
                # Update the max value
                if extreme_value < value:
                    extreme_value = value
                    best_move = move
                if beta < extreme_value:
                    # Prune the rest of children nodes, beta cutoff
                    # print('prune', 'beta-cutoff', depth)
                    self.prunes['beta', depth] += 1
                    return beta, best_move
        else:
            # Minimizing node
            extreme_value = beta
            for move in self.rollout_order(moves):
                self.simulator.restore_state(state)
                next_board, next_turn, next_last_moved_piece, next_moves, winner = self.simulator.move(*move, skip_check=True)
                # print(self.color == turn, depth, move, next_board)
                next_state = self.simulator.save_state()
                # Evaluate the next position
                value, _ = self.minimax_search(next_state, alpha, extreme_value, depth=depth-1, visited_states=visited_states)
                # Update the min value
                if value < extreme_value:
                    extreme_value = value
                    best_move = move
                if extreme_value < alpha:
                    # Prune the rest of children nodes, alpha cutoff
                    # print('prune', 'alpha-cutoff', depth)
                    self.prunes['alpha', depth] += 1
                    return alpha, best_move
        return extreme_value, best_move


def material_value(king_value, man_value, pieces):
    '''
    Zero-th order heuristics
    Heuristic based on advantage in material value
    1. Men are worth `man_value` per man
    1. Kings are worth `king_value` per king
    '''
    return man_value * len(pieces['men']) + king_value * len(pieces['kings'])


def material_value_adv(color, king_value, man_value, board, turn, last_moved_piece):
    black_adv = material_value(king_value, man_value, board['black']) - material_value(king_value, man_value, board['white'])
    return black_adv if color == 'black' else -black_adv


def board_value(color, advance_bonus, safety_bonus, pieces):
    '''
    First order heuristics
    Heuristic based on absolute placement on the board
    Using some ideas from section 5.1.3 on http://www.cs.huji.ac.il/~ai/projects/old/English-Draughts.pdf
    1. Advanced men are worth `advance_bonus` per man per *8 rows* (Easily to see the scales)
    2. Pieces on the edges are worth `safety_bonus` per piece

    Caution: using first order heuristics without zero-th order heuristics can produce bad behaviors, e.g., advanced men don't want to be crowned.
    '''
    value = 0
    for piece_type in Checkers.all_piece_types:
        for sq in pieces[piece_type]:
            # XXX Assuming the standard board (empty corner at upper left)
            row = sq // 4
            col = (sq % 4) * 2 + (row + 1) % 2
            # Advanced men
            if piece_type == 'men':
                if color == 'black':
                    # Greater row is better
                    advancement = row + 1
                else:
                    # White. Smaller row is better
                    advancement = 8 - row
                value += advancement / 8 * advance_bonus
            # Safe pieces
            if row == 0 or row == 7 or col == 0 or col == 7:
                value += safety_bonus
    return value


def first_order_adv(color, king_value, man_value, advance_bonus, safety_bonus, board, turn, last_moved_piece):
    black_adv = material_value(king_value, man_value, board['black'])
    black_adv += board_value('black', advance_bonus, safety_bonus, board['black'])
    black_adv -= material_value(king_value, man_value, board['white'])
    black_adv -= board_value('white', advance_bonus, safety_bonus, board['white'])
    return black_adv if color == 'black' else -black_adv


def pair_value(color, board):
    '''
    Second order heuristics
    Heuristic based on pairs of pieces' relative placements
    1. Given some perceived advantage, one should close in on the opponent's pieces.
    2. Conversely, one wants to avoid opponents (run away).
    '''
    # TODO
    pass


if __name__ == '__main__':
    from checkers.agents.baselines import play_a_game, RandomPlayer
    # from checkers.agents.baselines import keyboard_player_move

    # A few matches against a random player
    max_game_len = 200
    n_matches = 1
    n_wins, n_draws, n_losses = 0, 0, 0
    for i in range(n_matches):
        print('game', i)
        ch = Checkers()
        black_player = MinimaxPlayer(
            'black',
            value_func=partial(first_order_adv, 'black', 200, 100, 20, 0),
            # The provided legal moves might be ordered differently
            rollout_order_gen=lambda x: sorted(x),
            search_depth=4,
            seed=i)
        white_player = MinimaxPlayer('white', value_func=partial(material_value_adv, 'white', 2, 1), search_depth=4, seed=i * 2)
        white_player = RandomPlayer('white', seed=i * 2)
        winner = play_a_game(ch, black_player.next_move, white_player.next_move, max_game_len)
        # Play with a minimax player
        # play_a_game(ch, keyboard_player_move, white_player.next_move)
        print('black player evaluated %i positions in %.2fs (avg %.2f positions/s) effective branching factor %.2f' % (black_player.n_evaluated_positions, black_player.evaluation_dt, black_player.n_evaluated_positions / black_player.evaluation_dt, (black_player.n_evaluated_positions / black_player.ply) ** (1 / black_player.search_depth)))
        print('black player pruned', black_player.prunes.items())
        print()
        # Keep scores
        n_wins += 1 if winner == 'black' else 0
        n_draws += 1 if winner is None else 0
        n_losses += 1 if winner == 'white' else 0
    print('black win', n_wins, 'draw', n_draws, 'loss', n_losses)
