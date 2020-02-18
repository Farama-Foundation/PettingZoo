import gym
from gym.spaces import Box
from gym_backgammon.envs.backgammon import Backgammon as Game, WHITE, BLACK, COLORS
from random import randint
from gym_backgammon.envs.rendering import Viewer
import numpy as np

STATE_W = 96
STATE_H = 96

SCREEN_W = 600
SCREEN_H = 500


class BackgammonEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array', 'state_pixels']}

    def __init__(self):
        self.game = Game()
        self.current_agent = None

        low = np.zeros((198, 1))
        high = np.ones((198, 1))

        for i in range(3, 97, 4):
            high[i] = 6.0
        high[96] = 7.5

        for i in range(101, 195, 4):
            high[i] = 6.0
        high[194] = 7.5

        self.observation_space = Box(low=low, high=high)
        self.counter = 0
        self.max_length_episode = 10000
        self.viewer = None

    def step(self, action):
        self.game.execute_play(self.current_agent, action)

        # get the board representation from the opponent player perspective (the current player has already performed the move)
        observation = self.game.get_board_features(self.game.get_opponent(self.current_agent))

        reward = 0
        done = False

        winner = self.game.get_winner()

        if winner is not None or self.counter > self.max_length_episode:
            # practical-issues-in-temporal-difference-learning, pag.3
            # ...leading to a final reward signal z. In the simplest case, z = 1 if White wins and z = 0 if Black wins
            if winner == WHITE:
                reward = 1
            done = True

        self.counter += 1

        return observation, reward, done, winner

    def reset(self):
        # roll the dice
        roll = randint(1, 6), randint(1, 6)

        # roll the dice until they are different
        while roll[0] == roll[1]:
            roll = randint(1, 6), randint(1, 6)

        # set the current agent
        if roll[0] > roll[1]:
            self.current_agent = WHITE
            roll = (-roll[0], -roll[1])
        else:
            self.current_agent = BLACK

        self.game = Game()
        self.counter = 0

        return self.current_agent, roll, self.game.get_board_features(self.current_agent)

    def render(self, mode='human'):
        assert mode in ['human', 'rgb_array', 'state_pixels'], print(mode)

        if mode == 'human':
            self.game.render()
            return True
        else:
            if self.viewer is None:
                self.viewer = Viewer(SCREEN_W, SCREEN_H)

            if mode == 'rgb_array':
                width = SCREEN_W
                height = SCREEN_H

            else:
                assert mode == 'state_pixels', print(mode)
                width = STATE_W
                height = STATE_H

            return self.viewer.render(board=self.game.board, bar=self.game.bar, off=self.game.off, state_w=width, state_h=height)

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

    def get_valid_actions(self, roll):
        return self.game.get_valid_plays(self.current_agent, roll)

    def get_opponent_agent(self):
        self.current_agent = self.game.get_opponent(self.current_agent)
        return self.current_agent


class BackgammonEnvPixel(BackgammonEnv):

    def __init__(self):
        super(BackgammonEnvPixel, self).__init__()
        self.observation_space = Box(low=0, high=255, shape=(STATE_H, STATE_W, 3), dtype=np.uint8)

    def step(self, action):
        observation, reward, done, winner = super().step(action)
        observation = self.render(mode='state_pixels')
        return observation, reward, done, winner

    def reset(self):
        current_agent, roll, observation = super().reset()
        observation = self.render(mode='state_pixels')
        return current_agent, roll, observation
