import warnings

import chess
import numpy as np
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from . import chess_utils

"""
Chess is one of the oldest studied games in AI. Our implementation of the observation and action spaces for chess are what the AlphaZero method uses, with two small changes.

### Observation Space
* Channels 0 - 3: Castling rights:
  * Channel 0: All ones if white can castle queenside
  * Channel 1: All ones if white can castle kingside
  * Channel 2: All ones if black can castle queenside
  * Channel 3: All ones if black can castle kingside
* Channel 4: Is black or white
* Channel 5: A move clock counting up to the 50 move rule. Represented by a single channel where the *n* th element in the flattened channel is set if there has been *n* moves
* Channel 6: All ones to help neural networks find board edges in padded convolutions
* Channel 7 - 18: One channel for each piece type and player color combination. For example, there is a specific channel that represents black knights. An index of this channel is set to 1 if a black knight is in the corresponding spot on the game board, otherwise, it is set to 0. En passant possibilities are represented by displaying the vulnerable pawn on the 8th row instead of the 5th.
* Channel 19: represents whether a position has been seen before (whether a position is a 2-fold repetition)

### Action Space

From the AlphaZero chess paper:

> [In AlphaChessZero, the] action space is a 8x8x73 dimensional array.
Each of the 8×8 positions identifies the square from which to “pick up” a piece. The first 56 planes encode possible ‘queen moves’ for any piece: a number of squares [1..7] in which the piece will be
moved, along one of eight relative compass directions {N, NE, E, SE, S, SW, W, NW}. The
next 8 planes encode possible knight moves for that piece. The final 9 planes encode possible
underpromotions for pawn moves or captures in two possible diagonals, to knight, bishop or
rook respectively. Other pawn moves or captures from the seventh rank are promoted to a
queen.

We instead flatten this into 8×8×73 = 4672 discrete action space.

You can get back the original (x,y,c) coordinates from the integer action `a` with the following expression: `(a/(8*73), (a/73)%8, a%(8*8))`

### Rewards

"""

def env():
    env = raw_env()
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):

    metadata = {'render.modes': ['human'], "name": "chess_v5"}

    def __init__(self):
        super().__init__()

        self.board = chess.Board()

        self.agents = [f"player_{i}" for i in range(2)]
        self.possible_agents = self.agents[:]

        self._agent_selector = agent_selector(self.agents)

        self.action_spaces = {name: spaces.Discrete(8 * 8 * 73) for name in self.agents}
        self.observation_spaces = {name: spaces.Dict({
            'observation': spaces.Box(low=0, high=1, shape=(8, 8, 111), dtype=bool),
            'action_mask': spaces.Box(low=0, high=1, shape=(4672,), dtype=np.int8)
        }) for name in self.agents}

        self.rewards = None
        self.dones = None
        self.infos = {name: {} for name in self.agents}

        self.agent_selection = None

        self.board_history = np.zeros((8, 8, 104), dtype=bool)

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def observe(self, agent):
        observation = chess_utils.get_observation(self.board, self.possible_agents.index(agent))
        observation = np.dstack((observation[:, :, :7], self.board_history))
        legal_moves = chess_utils.legal_moves(self.board) if agent == self.agent_selection else []

        action_mask = np.zeros(4672, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def reset(self):
        self.has_reset = True

        self.agents = self.possible_agents[:]

        self.board = chess.Board()

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        self.rewards = {name: 0 for name in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        self.dones = {name: False for name in self.agents}
        self.infos = {name: {} for name in self.agents}

        self.board_history = np.zeros((8, 8, 104), dtype=bool)

    def set_game_result(self, result_val):
        for i, name in enumerate(self.agents):
            self.dones[name] = True
            result_coef = 1 if i == 0 else -1
            self.rewards[name] = result_val * result_coef
            self.infos[name] = {'legal_moves': []}

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        current_agent = self.agent_selection
        current_index = self.agents.index(current_agent)
        next_board = chess_utils.get_observation(self.board, current_agent)
        self.board_history = np.dstack((next_board[:, :, 7:], self.board_history[:, :, :-13]))
        self.agent_selection = self._agent_selector.next()

        chosen_move = chess_utils.action_to_move(self.board, action, current_index)
        assert chosen_move in self.board.legal_moves
        self.board.push(chosen_move)

        next_legal_moves = chess_utils.legal_moves(self.board)

        is_stale_or_checkmate = not any(next_legal_moves)

        # claim draw is set to be true to align with normal tournament rules
        is_repetition = self.board.is_repetition(3)
        is_50_move_rule = self.board.can_claim_fifty_moves()
        is_claimable_draw = is_repetition or is_50_move_rule
        game_over = is_claimable_draw or is_stale_or_checkmate

        if game_over:
            result = self.board.result(claim_draw=True)
            result_val = chess_utils.result_to_int(result)
            self.set_game_result(result_val)

        self._accumulate_rewards()

    def render(self, mode='human'):
        print(self.board)
        return str(self.board)

    def close(self):
        pass
