from pettingzoo import AECEnv
from gym import spaces
import numpy as np
import warnings

from .manual_control import manual_control


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
        self.agents = ['player_0', 'player_1']

        self.agent_order = list(self.agents)

        self.action_spaces = {i: spaces.Discrete(7) for i in range(2)}
        self.observation_spaces = {i: spaces.Box(low=0, high=2, shape=(6, 7), dtype=np.int8) for i in range(2)}

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': list(range(7))} for i in range(self.num_agents)}

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

    # action in this case is a value from 0 to 6 indicating position to move on the flat representation of the connect4 board
    def step(self, action, observe=True):
        # check if input action is a valid move (0 == empty spot)
        if(self.board[0:7][action] == 0):
            # valid move
            for i in list(filter(lambda x: x % 7 == action, list(range(41, -1, -1)))):
                if self.board[i] == 0:
                    self.board[i] = self.agent_selection + 1
                    break

            next_agent = 1 if (self.agent_selection == 0) else 0

            # update infos with valid moves
            self.infos[self.agent_selection]['legal_moves'] = [i for i in range(7) if self.board[i] == 0]
            self.infos[next_agent]['legal_moves'] = [i for i in range(7) if self.board[i] == 0]

            winner = self.check_for_winner()

            # check if there is a winner
            if winner:
                self.rewards[self.agent_selection] += 1
                self.rewards[next_agent] -= 1
                self.dones = {i: True for i in range(self.num_agents)}
            # check if there is a tie
            elif all(x in [1, 2] for x in self.board):
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
        self.infos = {i: {'legal_moves': list(range(7))} for i in range(self.num_agents)}

        # selects the first agent
        self.agent_selection = 0
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def render(self, mode='ansi'):
        print(str(self.observe(self.agent_selection)))

    def close(self):
        pass

    def check_for_winner(self):
        board = np.array(self.board).reshape(6, 7)
        piece = self.agent_selection + 1

        # Check horizontal locations for win
        column_count = 7
        row_count = 6

        for c in range(column_count - 3):
            for r in range(row_count):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                    return True

        # Check vertical locations for win
        for c in range(column_count):
            for r in range(row_count - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                    return True

        # Check positively sloped diaganols
        for c in range(column_count - 3):
            for r in range(row_count - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diaganols
        for c in range(column_count - 3):
            for r in range(3, row_count):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                    return True

        return False
