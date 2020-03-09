from pettingzoo.utils import AECEnv, agent_selector
from gym import spaces
import numpy as np

# A few baseline players for Checkers including a keyboard player
from __future__ import absolute_import, division, print_function

from checkers.game import Checkers, Player

# A random player
class RandomPlayer(Player):
    '''A player that makes random legal moves.'''

    def next_move(self, board, last_moved_piece):
        state = (board, self.color, last_moved_piece)
        self.simulator.restore_state(state)
        legal_moves = self.simulator.legal_moves()
        move = self.random.choice(np.asarray(legal_moves, dtype='int,int'))
        return move


class env(AECEnv):
    # metadata = {'render.modes': ['human']} # only add if environment supports rendering

    def __init__(self): # continuous=False, vector_observation=True
        super(env, self).__init__()

        self.agents = [RandomPlayer('black', seed=0), RandomPlayer('white', seed=2)] 
        self.agent_order = [0, 1]
        self._agent_selector = agent_selector(self.agent_order)

        self.rewards = {0: 0, 1: 0}
        self.dones = {0: False, 1: False}
        self.infos = {0: None, 1: None}

        self.reset()

        self.observation_spaces = {}
        self.action_spaces = {}

        self.max_plies=float('inf')
        self.ch = Checkers()
        self.board = None

    def observe(self, agent):
        # return observation of an agent
        return observation
    
    def step(self, actions, observe = True):
        
        agent = self.agent_selection
        reward = 0

        if action != None:
            if action != 0 and not self.continuous:
                action = action/abs(action)
            reward = self.

        self.tot_moves += len(actions)
        # The current game state
        self.ch.print_board()
        print(self.ply, 'turn:', self.turn, 'last_moved_piece:', self.last_moved_piece)
        print('%i legal moves %r' % (len(actions), actions))
        # Select a legal move for the current player
        from_sq, to_sq = players[self.turn](self.board, self.last_moved_piece)
        print(self.turn, 'moved %i, %i' % (from_sq, to_sq))
        print()
        # Update the game
        self.board, self.turn, self.last_moved_piece, actions, self.winner = self.ch.move(from_sq, to_sq)
        self.ply += 1
        # Switch selection to next agents
        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)
        

    def reset(self, observe = True):
        # reset environment
        self.num_moves = 0
        self.ply = 0
        self.tot_moves = 0
        self.turn = 'black'
        self.moves = None
        self.last_moved_piece = None
        self.ch.print_empty_board()
        self.winner = None

        # selects the first agent
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)


    def render(self, mode = 'human'):
        pass

    def close(self):
        pass
    

    def play_a_game(self):
        # Play a quick game
        players = {
        'black': self.agents[0].next_move,
        'white': self.agents[1].next_move,
        }
        self.board, self.turn, self.last_moved_piece = self.ch.save_state()
        self.moves = self.ch.legal_moves()

        while self.winner is None and self.ply < self.max_plies:
            self.step()

        if self.winner is None:
            print('draw')
        else:
            print('%s player wins' % self.winner)
        print('total legal moves', self.tot_moves, 'avg branching factor', self.tot_moves / self.ply)






