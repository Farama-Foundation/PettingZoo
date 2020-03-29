from pettingzoo import AECEnv
from gym import spaces

import numpy as np

import warnings

class env(AECEnv):
    metadata = {'render.modes': ['ansi']}

    def __init__(self):
        super(env, self).__init__()
        # 6 rows x 7 columns
        # blank space = 0
        # agent 0 -- 1
        # agent 1 -- 2
        # flat representation in row major order
        self.board = [0] * (6 * 7)

        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.agent_order = list(self.agents)

        self.action_spaces = {i: spaces.Discrete(6 * 7) for i in range(2)}
        self.observation_spaces = {i: spaces.Box(low=0, high=2, shape=(6, 7), dtype=np.int8) for i in range(2)}

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': list(range(0, len(self.board)))} for i in range(self.num_agents)}

        self.agent_selection = 0

    # Key
    # ----
    # blank space = 0
    # agent 0 = 1
    # agent 1 = 2
    # An observation is list of lists, where each list represents a row
    #
    # array([[0, 1, 1, 2, 0, 1, 0],
    #        [1, 0, 1, 2, 2, 2, 1],
    #        [0, 1, 0, 0, 1, 2, 1],
    #        [1, 0, 2, 0, 1, 1, 0],
    #        [2, 0, 0, 0, 1, 1, 0],
    #        [1, 1, 2, 1, 0, 1, 0]], dtype=int8)
    def observe(self, agent):
        return np.array(self.board).reshape(6, 7)

    # action in this case is a value from 0 to 42 indicating position to move on the flat representation of the connect4 board
    def step(self, action, observe=True):
        # check if input action is a valid move (0 == empty spot)
        if(self.board[action] == 0):
            # valid move
            self.board[action] = self.agent_selection + 1

            next_agent = 1 if (self.agent_selection == 0) else 0

            # update infos with valid moves
            self.infos[self.agent_selection]['legal_moves'] = [i for i in range(len(self.board)) if self.board[i] == 0]
            self.infos[next_agent]['legal_moves'] = [i for i in range(len(self.board)) if self.board[i] == 0]

            winner = self.check_for_winner()

            # check if there is a winner
            if winner:
                self.rewards[self.agent_selection] += 1
                self.rewards[next_agent] -= 1
                self.dones = {i: True for i in range(self.num_agents)}
            # check if there is a tie
            elif all(x in [1, 2] for x in self.board):
                print("tie")
                # once either play wins or there is a draw, game over, both players are done
                self.dones = {i: True for i in range(self.num_agents)}
            else:
                # no winner yet
                self.agent_selection = next_agent

        else:
            # invalid move, end game
            self.rewards[self.agent_selection] -= 1
            self.dones = {i: True for i in range(self.num_agents)}
            warnings.warn("Bad connect four move made, game terminating with current player losing. env.infos[player]['legal_moves'] contains a list of all legal moves that can be chosen.")

        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def reset(self, observe=True):
        # reset environment
        self.board = [0] * (6 * 7)

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': list(range(0, 6 * 7))} for i in range(self.num_agents)}

        # selects the first agent
        self.agent_selection = 0
        if observe:
            return self.observe(self.agent_selection)
        else:
            return
    
    def render(self, mode='human'):
        print(str(self.observe(self.agent_selection)))

    def close(self):
        pass

    # return 0 for no winner
    # return 1 for agent 0
    # return 2 for agent 1
    def check_for_winner(self):
        return 0

# import pettingzoo as pz
# env = pz.classic.connect_four.env()

# import pettingzoo as pz
# env = pz.classic.connect_four.manual_control()