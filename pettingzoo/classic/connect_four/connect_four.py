import os

import numpy as np
import pygame
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector


def get_image(path):
    from os import path as os_path

    import pygame
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


def env():
    env = raw_env()
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    metadata = {
        "render.modes": ["human", "rgb_array"],
        "name": "connect_four_v3",
        "is_parallelizable": False,
        "video.frames_per_second": 2,
    }

    def __init__(self):
        super().__init__()
        # 6 rows x 7 columns
        # blank space = 0
        # agent 0 -- 1
        # agent 1 -- 2
        # flat representation in row major order
        self.screen = None

        self.board = [0] * (6 * 7)

        self.agents = ['player_0', 'player_1']
        self.possible_agents = self.agents[:]

        self.action_spaces = {i: spaces.Discrete(7) for i in self.agents}
        self.observation_spaces = {i: spaces.Dict({
            'observation': spaces.Box(low=0, high=1, shape=(6, 7, 2), dtype=np.int8),
            'action_mask': spaces.Box(low=0, high=1, shape=(7,), dtype=np.int8)
        }) for i in self.agents}

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
        board_vals = np.array(self.board).reshape(6, 7)
        cur_player = self.possible_agents.index(agent)
        opp_player = (cur_player + 1) % 2

        cur_p_board = np.equal(board_vals, cur_player + 1)
        opp_p_board = np.equal(board_vals, opp_player + 1)

        observation = np.stack([cur_p_board, opp_p_board], axis=2).astype(np.int8)
        legal_moves = self._legal_moves() if agent == self.agent_selection else []

        action_mask = np.zeros(7, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _legal_moves(self):
        return [i for i in range(7) if self.board[i] == 0]

    # action in this case is a value from 0 to 6 indicating position to move on the flat representation of the connect4 board
    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        # assert valid move
        assert (self.board[0:7][action] == 0), "played illegal move."

        piece = self.agents.index(self.agent_selection) + 1
        for i in list(filter(lambda x: x % 7 == action, list(range(41, -1, -1)))):
            if self.board[i] == 0:
                self.board[i] = piece
                break

        next_agent = self._agent_selector.next()

        winner = self.check_for_winner()

        # check if there is a winner
        if winner:
            self.rewards[self.agent_selection] += 1
            self.rewards[next_agent] -= 1
            self.dones = {i: True for i in self.agents}
        # check if there is a tie
        elif all(x in [1, 2] for x in self.board):
            # once either play wins or there is a draw, game over, both players are done
            self.dones = {i: True for i in self.agents}
        else:
            # no winner yet
            self.agent_selection = next_agent

        self._accumulate_rewards()

    def reset(self):
        # reset environment
        self.board = [0] * (6 * 7)

        self.agents = self.possible_agents[:]
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        self.dones = {i: False for i in self.agents}
        self.infos = {i: {} for i in self.agents}

        self._agent_selector = agent_selector(self.agents)

        self.agent_selection = self._agent_selector.reset()

    def render(self, mode='human'):
        screen_width = 1287
        screen_height = 1118
        if self.screen is None:
            if mode == "human":
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))
            else:
                self.screen = pygame.Surface((screen_width, screen_height))
        if mode == "human":
            pygame.event.get()

        # Load and scale all of the necessary images
        tile_size = (screen_width * (91 / 99)) / 7

        red_chip = get_image(os.path.join('img', 'C4RedPiece.png'))
        red_chip = pygame.transform.scale(red_chip, (int(tile_size * (9 / 13)), int(tile_size * (9 / 13))))

        black_chip = get_image(os.path.join('img', 'C4BlackPiece.png'))
        black_chip = pygame.transform.scale(black_chip, (int(tile_size * (9 / 13)), int(tile_size * (9 / 13))))

        board_img = get_image(os.path.join('img', 'Connect4Board.png'))
        board_img = pygame.transform.scale(board_img, ((int(screen_width)), int(screen_height)))

        self.screen.blit(board_img, (0, 0))

        # Blit the necessary chips and their positions
        for i in range(0, 42):
            if self.board[i] == 1:
                self.screen.blit(red_chip, ((i % 7) * (tile_size) + (tile_size * (6 / 13)), int(i / 7) * (tile_size) + (tile_size * (6 / 13))))
            elif self.board[i] == 2:
                self.screen.blit(black_chip, ((i % 7) * (tile_size) + (tile_size * (6 / 13)), int(i / 7) * (tile_size) + (tile_size * (6 / 13))))

        if mode == "human":
            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None

    def close(self):
        if self.screen is not None:
            import pygame
            pygame.quit()
            self.screen = None

    def check_for_winner(self):
        board = np.array(self.board).reshape(6, 7)
        piece = self.agents.index(self.agent_selection) + 1

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

        # Check positively sloped diagonals
        for c in range(column_count - 3):
            for r in range(row_count - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(column_count - 3):
            for r in range(3, row_count):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                    return True

        return False
