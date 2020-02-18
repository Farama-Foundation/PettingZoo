# Monte Carlo tree search
from __future__ import absolute_import, division, print_function

import itertools
from collections import defaultdict

import numpy as np

from checkers.game import Checkers
from checkers.agents import Player


class MctsPlayer(Player):
    '''
    Monte Carlo Tree Search player with upper confidence bound (UCB1)
    references:
    https://www.cs.swarthmore.edu/~bryce/cs63/s16/slides/2-17_extending_mcts.pdf
    _A Survey of Monte Carlo Tree Search Methods_ http://mcts.ai/pubs/mcts-survey-master.pdf
    '''

    def __init__(self, color, exploration_coeff=1, max_rounds=800, max_plies=float('inf'), discount=0.99, seed=None):
        super(MctsPlayer, self).__init__(color=color, seed=seed)

        # Default policy for rollouts
        self.rollout_policy = lambda moves: self.random.choice(np.asarray(moves, dtype='int,int'))
        # Maximum plies in each rollout
        self.max_plies = max_plies
        # Maximum rounds of simulation
        self.max_rounds = max_rounds
        # Explore
        self.exploration_coeff = exploration_coeff
        # Discount for the reward
        self.discount = discount

        # Checkers can draw. Should keep the win counts separately for each player in general
        self.stats = defaultdict(lambda: (0, 0, 0))
        self.children = defaultdict(lambda: set())

    def q(self, turn, st):
        # XXX compute Q for each player. Both try to maximize its own value
        black_wins, white_wins, n_samples = self.stats[st]
        next_q = black_wins / n_samples if turn == 'black' else white_wins / n_samples
        return next_q

    @staticmethod
    def successor(st):
        sim = Checkers()
        state = MctsPlayer.convert_to_state(st)
        sim.restore_state(state)
        next_sts = []
        moves = sorted(sim.legal_moves())
        for move in moves:
            sim.restore_state(state)
            board, turn, last_moved_piece, _, winner = sim.move(*move)
            next_state = board, turn, last_moved_piece
            next_st = MctsPlayer.immutable_state(*next_state)
            next_sts.append(next_st)
        return next_sts

    def next_move(self, board, last_moved_piece):
        # Initialize with root node
        st0 = MctsPlayer.immutable_state(board, self.color, last_moved_piece)

        round = 0
        while round < self.max_rounds:
            # Start from the root
            st = st0
            walked_sts = [st]

            # Selection
            # XXX search could be stuck in a loop here (when are very possible successors left)
            succ_sts = MctsPlayer.successor(st)
            while 0 < len(succ_sts) and len(succ_sts) == len(self.children[st]):
                # Not a terminal state and all children are expanded
                # Use tree policy, choose a successor according to according to Q_hat + UCB
                max_score = float('-inf')
                max_st = None
                turn = st[1]
                for next_st in self.children[st]:
                    # Upper confidence bound
                    next_q = self.q(turn, next_st) + self.exploration_coeff * MctsPlayer.ucb(self.stats[st][-1], self.stats[next_st][-1])
                    if max_score < next_q:
                        max_score = next_q
                        max_st = next_st
                st = max_st
                # Loop detection
                if st in walked_sts:
                    break
                # Add it to walked states in this round
                walked_sts.append(st)
                succ_sts = MctsPlayer.successor(st)

            # Expansion
            # Not an internal node, choose a successor state randomly
            succ_sts = MctsPlayer.successor(st)
            if 0 < len(succ_sts):
                # Not a terminal state
                next_idx = self.random.randint(len(succ_sts))
                next_st = succ_sts[next_idx]
                walked_sts.append(next_st)
                # Add this node to the tree
                self.children[st].add(next_st)
                st = next_st

            # Simulation
            # Rollout till the game ends with a default policy
            winner, ply = self.rollout(st)

            # Back-propagation
            # Update statistics on the walked nodes
            reward = self.discount ** ply
            for st in reversed(walked_sts):
                black_wins, white_wins, n_samples = self.stats[st]
                turn = st[1]
                # Update wins based on the turn
                black_wins += reward if winner == 'black' else 0
                white_wins += reward if winner == 'white' else 0
                self.stats[st] = black_wins, white_wins, n_samples + 1
                # This reduces the influence of lucky rollouts due to very long random rollout
                reward *= self.discount
            round += 1

        # Select a move after searching
        # print(len(self.children[st0]))
        sim = Checkers()
        state = MctsPlayer.convert_to_state(st0)
        sim.restore_state(state)
        moves = sorted(sim.legal_moves())
        # Q-maximizing move
        max_q, max_q_move = float('-inf'), None
        # Visit-maximizing move
        max_n, max_n_move = float('-inf'), None
        for move in moves:
            sim.restore_state(state)
            board, turn, last_moved_piece, _, _ = sim.move(*move)
            next_st = MctsPlayer.immutable_state(board, turn, last_moved_piece)
            if next_st in self.children[st0]:
                # Maximize Q for the player
                next_q = self.q(self.color, next_st)
                if max_q < next_q:
                    max_q = next_q
                    max_q_move = move
                n_samples = self.stats[next_st][-1]
                if max_n < n_samples:
                    max_n = n_samples
                    max_n_move = move
                # print(move, '%.2f' % next_q, n_samples, next_st[1], self.stats[next_st], self.stats[next_st][0] + self.stats[next_st][1] - self.stats[next_st][-1])
        # Print some statistics
        print('V_hat(player) - V_hat(opponent) = %.2f' % (self.q(self.color, st0) - self.q('white' if self.color == 'black' else 'black', st0)))
        leaf_counts = MctsPlayer.hist_leaf_depth(self.children, st0)
        print('leaf depth histogram (depth, count):', sorted(leaf_counts.items()), 'max depth', max(leaf_counts.keys()))
        return max_q_move

    @staticmethod
    def immutable_state(board, turn, last_moved_piece):
        return Checkers.immutable_board(board), turn, last_moved_piece

    @staticmethod
    def hist_leaf_depth(children, root_st):
        '''Returns counts of leaves at different depths'''
        counts = defaultdict(lambda: 0)
        # Breadth first iteration
        queue = [(root_st, 0)]
        # XXX be careful with loops in a graph
        visited = set()
        while 0 < len(queue):
            st, depth = queue.pop(0)
            if st in visited:
                # Found a loop
                continue
            visited.add(st)
            if 0 == len(children[st]):
                # A leaf node
                counts[depth] += 1
            else:
                # Internal node, expand
                queue += itertools.product(children[st], [depth + 1])
        return counts

    @staticmethod
    def convert_to_state(st):
        bo, turn, last_moved_piece = st
        black_men, black_kings, white_men, white_kings = bo
        board = {
            'black': {
                'men': set(black_men),
                'kings': set(black_kings),
                },
            'white': {
                'men': set(white_men),
                'kings': set(white_kings),
            },
        }
        return board, turn, last_moved_piece

    def rollout(self, st):
        '''Rollout till the game ends with a win/draw'''
        sim = Checkers()
        state = MctsPlayer.convert_to_state(st)
        sim.restore_state(state)
        ply = 0
        moves = sim.legal_moves()
        # Check for a terminal state
        if len(moves) == 0:
            # One player wins
            winner = 'white' if st[1] == 'black' else 'black'
        else:
            winner = None
        while ply < self.max_plies and winner is None:
            from_sq, to_sq = self.rollout_policy(moves)
            board, turn, last_moved_piece, moves, winner = sim.move(from_sq, to_sq, skip_check=True)
            ply += 1
        # Returns the winner or None in a draw
        return winner, ply

    @staticmethod
    def ucb(n_parent_visits, n_visits):
        '''Upper confidence bound (UCB1) based on Hoeffding inequality'''
        return np.sqrt(2 * np.log(n_parent_visits) / n_visits)


if __name__ == '__main__':
    from checkers.agents.baselines import play_a_game
    from checkers.agents.alpha_beta import MinimaxPlayer

    # End game
    # _._._._.
    # ._._._._
    # _._._._.
    # ._W_._._
    # _._._._.
    # ._._._._
    # _._B_._.
    # ._._._._
    # bo = Checkers.empty_board()
    # bo['black']['kings'].add(25)
    # bo['white']['kings'].add(13)
    # ch = Checkers(board=bo, turn='white', last_moved_piece=None)
    ch = Checkers()
    # black_player = RandomPlayer('black')
    black_player = MinimaxPlayer(
        color='black',
        # The provided legal moves might be ordered differently
        search_depth=5,
        seed=0,
        )
    white_player = MctsPlayer(
        color='white',
        exploration_coeff=1,
        max_rounds=400,
        seed=1,
        )
    play_a_game(ch, black_player.next_move, white_player.next_move)
