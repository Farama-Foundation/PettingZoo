from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from gym import spaces
import numpy as np
import warnings

from pettingzoo.utils import wrappers

from .board import Board


def env():
    env = raw_env()
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NaNRandomWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super().__init__()
        self.board = Board()

        self.num_agents = 2
        self.agents = ["player_1", "player_2"]

        self.agent_order = list(self.agents)

        self.action_spaces = {i: spaces.Discrete(9) for i in self.agents}
        self.observation_spaces = {i: spaces.Box(low=0, high=1, shape=(3, 3, 2), dtype=np.int8) for i in self.agents}

        self.rewards = {i: 0 for i in self.agents}
        self.dones = {i: False for i in self.agents}
        self.infos = {i: {'legal_moves': list(range(0, 9))} for i in self.agents}

        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.reset()

    # Key
    # ----
    # blank space = 0
    # agent 0 = 1
    # agent 1 = 2
    # An observation is list of lists, where each list represents a row
    #
    # [[0,0,2]
    #  [1,2,1]
    #  [2,1,0]]
    def observe(self, agent):
        board_vals = np.array(self.board.squares).reshape(3, 3)
        cur_player = self.agents.index(self.agent_selection)
        opp_player = (cur_player + 1) % 2

        cur_p_board = np.equal(board_vals, cur_player + 1)
        opp_p_board = np.equal(board_vals, opp_player + 1)
        return np.stack([cur_p_board, opp_p_board], axis=2).astype(np.int8)

    # action in this case is a value from 0 to 8 indicating position to move on tictactoe board
    def step(self, action, observe=True):
        # check if input action is a valid move (0 == empty spot)
        assert (self.board.squares[action] == 0), "played illegal move"
        # play turn
        self.board.play_turn(self.agents.index(self.agent_selection), action)

        # update infos
        # list of valid actions (indexes in board)
        # next_agent = self.agents[(self.agents.index(self.agent_selection) + 1) % len(self.agents)]
        next_agent = self._agent_selector.next()
        self.infos[self.agent_selection]['legal_moves'] = [i for i in range(len(self.board.squares)) if self.board.squares[i] == 0]
        self.infos[next_agent]['legal_moves'] = [i for i in range(len(self.board.squares)) if self.board.squares[i] == 0]

        if self.board.check_game_over():
            winner = self.board.check_for_winner()

            if winner == -1:
                # tie
                pass
            elif winner == 1:
                # agent 0 won
                self.rewards[self.agents[0]] += 1
                self.rewards[self.agents[1]] -= 1
            else:
                # agent 1 won
                self.rewards[self.agents[1]] += 1
                self.rewards[self.agents[0]] -= 1

            # once either play wins or there is a draw, game over, both players are done
            self.dones = {i: True for i in self.agents}

        # Switch selection to next agents
        self.agent_selection = next_agent

        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def reset(self, observe=True):
        # reset environment
        self.board = Board()

        self.rewards = {i: 0 for i in self.agents}
        self.dones = {i: False for i in self.agents}
        self.infos = {i: {'legal_moves': list(range(0, 9))} for i in self.agents}

        # selects the first agent
        self._agent_selector.reset()
        self.agent_selection = self._agent_selector.reset()
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def render(self, mode='human'):
        def getSymbol(input):
            if input == 0:
                return '-'
            elif input == 1:
                return 'X'
            else:
                return 'O'

        board = list(map(getSymbol, self.board.squares))

        print(" " * 5 + "|" + " " * 5 + "|" + " " * 5)
        print(f"  {board[0]}  " + "|" + f"  {board[3]}  " + "|" + f"  {board[6]}  ")
        print("_" * 5 + "|" + "_" * 5 + "|" + "_" * 5)

        print(" " * 5 + "|" + " " * 5 + "|" + " " * 5)
        print(f"  {board[1]}  " + "|" + f"  {board[4]}  " + "|" + f"  {board[7]}  ")
        print("_" * 5 + "|" + "_" * 5 + "|" + "_" * 5)

        print(" " * 5 + "|" + " " * 5 + "|" + " " * 5)
        print(f"  {board[2]}  " + "|" + f"  {board[5]}  " + "|" + f"  {board[8]}  ")
        print(" " * 5 + "|" + " " * 5 + "|" + " " * 5)

    def close(self):
        pass
