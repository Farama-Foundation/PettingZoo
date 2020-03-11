from . import chess_utils
import chess
from pettingzoo.utils import AECEnv
from gym import spaces
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(env, self).__init__()

        self.board = chess.Board()

        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.agent_order = list(self.agents)

        self.action_spaces = {i: spaces.Box(low=-np.inf, high=+np.inf, shape=(8, 8, 73), dtype=np.float32) for i in range(2)}
        self.observation_spaces = {i: spaces.Box(low=-np.inf, high=+np.inf, shape=(8, 8, 20), dtype=np.float32) for i in range(2)}

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {} for i in range(self.num_agents)}

        self.agent_selection = 0

        self.reset()

    def observe(self, agent):
        return chess_utils.get_observation(self.board, agent)

    def reset(self, observe=True):
        self.board = chess.Board()

        self.agent_selection = 0

        if observe:
            return self.observe(0)
        else:
            return

    def step(self, action, observe=True):
        current_idx = self.agent_selection
        self.agent_selection = next_agent = (self.agent_selection + 1) % self.num_agents

        sampled_move = chess_utils.sample_action(self.board, action)
        reoriented_move = sampled_move if not current_idx else chess_utils.mirror_move(sampled_move)

        self.board.push(reoriented_move)

        # claim draw is set to be true to allign with normal tournament rules
        if self.board.is_game_over(claim_draw=True):
            result = self.board.result(claim_draw=True)
            result_val = chess_utils.result_to_int(result)
            for i in range(2):
                self.dones[i] = True
                result_coef = 1 if i == 0 else -1
                self.rewards[i] = result_val * result_coef

        if observe:
            next_observation = self.observe(next_agent)
        else:
            next_observation = None
        return next_observation

    def render(self, mode='human'):
        print(self.board.board_fen())

    def close(self):
        pass
