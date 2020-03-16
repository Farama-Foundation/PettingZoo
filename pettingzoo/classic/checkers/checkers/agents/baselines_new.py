# A few baseline players for Checkers including a keyboard player
from __future__ import absolute_import, division, print_function

import numpy as np

from checkers.game import Checkers
from checkers.agents import Player

from pettingzoo import AECEnv
#from ray.rllib.env.multi_agent_env import MultiAgentEnvfrom ray import tune
#from ray.rllib.agents.pg.pg import PGTrainer
#from ray.rllib.agents.pg.pg_tf_policy import PGTFPolicy
#from ray.rllib.policy.policy import Policy

# A random player
class RandomPlayer(Player):
    '''A player that makes random legal moves.'''

    def next_move(self, board, last_moved_piece):
        state = (board, self.color, last_moved_piece)
        self.simulator.restore_state(state)
        legal_moves = self.simulator.legal_moves()
        move = self.random.choice(np.asarray(legal_moves, dtype='int,int'))
        return move

# Multi-agent environment
class env(AECEnv):

    def __init__(self):
        self.num_agents = 2
        self.agent_ids = list(range(self.num_agents))
        self.player1 = RandomPlayer('black', seed=0)
        self.player2 = RandomPlayer('white', seed=2) 
        self.winner = None
        self.max_plies=float('inf')
        self.ch = Checkers()
        self.board = None
        

    def start_status(self):
        self.num_moves = 0
        self.ply = 0
        self.tot_moves = 0
        self.turn = 'black'
        self.moves = None
        self.last_moved_piece = None
        self.ch.print_empty_board()

    def reset(self):
        self.start_status()

    def play_a_game(self):
        # Play a quick game
        players = {
            'black': self.player1.next_move,
            'white': self.player2.next_move,
        }
        self.board, self.turn, self.last_moved_piece = self.ch.save_state()
        self.moves = self.ch.legal_moves()
        while self.winner is None and self.ply < self.max_plies:
            self.tot_moves += len(self.moves)
            # The current game state
            self.ch.print_board()
            print(self.ply, 'turn:', self.turn, 'last_moved_piece:', self.last_moved_piece)
            print('%i legal moves %r' % (len(self.moves), self.moves))
            # Select a legal move for the current player
            from_sq, to_sq = players[self.turn](self.board, self.last_moved_piece)
            print(self.turn, 'moved %i, %i' % (from_sq, to_sq))
            print()
            # Update the game
            self.board, self.turn, self.last_moved_piece, self.moves, self.winner = self.ch.move(from_sq, to_sq)
            self.ply += 1
        if self.winner is None:
            print('draw')
        else:
            print('%s player wins' % self.winner)
        print('total legal moves', self.tot_moves, 'avg branching factor', self.tot_moves / self.ply)
    
    #def step(self, actions):
    #    for i, agent_id in enumerate(self.agents):


def run_same_policy():
    tune.run("PG", config={"env": RockPaperScissorsEnv})

if __name__ == '__main__':
    
    run_same_policy()

