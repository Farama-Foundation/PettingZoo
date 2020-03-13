from . import chess_utils
import chess
from pettingzoo.utils import AECEnv
from gym import spaces
import numpy as np
import warnings


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(env, self).__init__()

        self.board = chess.Board()

        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.agent_order = list(self.agents)

        self.action_spaces = {i: spaces.Discrete(8 * 8 * 73) for i in range(2)}
        self.observation_spaces = {i: spaces.Box(low=-np.inf, high=+np.inf, shape=(8, 8, 20), dtype=np.float32) for i in range(2)}

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': []} for i in range(self.num_agents)}

        self.agent_selection = 0

        self.reset()

    def observe(self, agent):
        return chess_utils.get_observation(self.board, agent)

    def reset(self, observe=True):
        self.board = chess.Board()

        self.agent_selection = 0

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': []} for i in range(self.num_agents)}
        self.infos[self.agent_selection]['legal_moves'] = chess_utils.legal_moves(self.board)

        if observe:
            return self.observe(0)
        else:
            return

    def set_game_result(self, result_val):
        for i in range(2):
            self.dones[i] = True
            result_coef = 1 if i == 0 else -1
            self.rewards[i] = result_val * result_coef
            self.infos[i] = {'legal_moves': []}

    def step(self, action, observe=True):
        current_idx = self.agent_selection
        self.agent_selection = next_agent = (self.agent_selection + 1) % self.num_agents

        old_legal_moves = self.infos[current_idx]['legal_moves']

        if action not in old_legal_moves:
            warnings.warn("Bad chess move made, game terminating with current player losing. \nenv.infos[player]['legal_moves'] contains a list of all legal moves that can be chosen.")
            player_loses_val = -1 if current_idx == 0 else 1
            self.set_game_result(player_loses_val)
        else:
            chosen_move = chess_utils.action_to_move(action, current_idx)

            self.board.push(chosen_move)

            # claim draw is set to be true to allign with normal tournament rules
            if self.board.is_game_over(claim_draw=True):
                result = self.board.result(claim_draw=True)
                result_val = chess_utils.result_to_int(result)
                self.set_game_result(result_val)
            else:
                self.infos[current_idx] = {'legal_moves': []}
                self.infos[next_agent] = {'legal_moves': chess_utils.legal_moves(self.board)}
                assert len(self.infos[next_agent]['legal_moves'])

        if observe:
            next_observation = self.observe(next_agent)
        else:
            next_observation = None
        return next_observation

    def render(self, mode='human'):
        print(self.board.board_fen())

    def close(self):
        pass
