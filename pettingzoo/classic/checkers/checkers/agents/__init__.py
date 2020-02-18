from __future__ import absolute_import, division, print_function


import numpy as np

from checkers.game import Checkers


class Player(object):
    '''An abstract player.'''

    def __init__(self, color, seed=None):
        assert color in Checkers.all_players, '`color` must be in %r.' % Checkers.all_players

        # Which side is being played
        self.color = color
        # Internal simulator for rollouts
        self.simulator = Checkers()
        # Fixing the random state for easy replications
        self.random = np.random.RandomState(seed=seed)

    def next_move(self, board, last_moved_piece):
        raise NotImplementedError
