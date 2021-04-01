from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from .backgammon import Backgammon as Game, WHITE, BLACK, COLORS
from gym import spaces
from . import bg_utils
import numpy as np


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    metadata = {'render.modes': ['human'], "name": "backgammon_v3"}

    def __init__(self):
        super().__init__()
        self.game = Game()
        self.seed()

        self.agents = ["player_{}".format(i) for i in range(2)]
        self.possible_agents = self.agents[:]
        self._agent_order = list(self.agents)
        self._agent_selector = agent_selector(self._agent_order)
        self.infos = {i: {} for i in self.agents}

        self.action_spaces = {name: spaces.Discrete(26 * 26 * 2 + 1) for name in self.agents}

        low = np.zeros((198,))
        high = np.ones((198,))
        for i in range(3, 97, 4):
            high[i] = 6.0
        high[96] = 7.5
        for i in range(101, 195, 4):
            high[i] = 6.0
        high[194] = 7.5
        self.observation_spaces = {
            i: spaces.Dict({'observation': spaces.Box(low=np.float32(low), high=np.float32(high), dtype=np.float32),
                            'action_mask': spaces.Box(low=0, high=1, shape=(1353,), dtype=np.int8)})
            for i in self.agents}
        self.double_roll = 0

    def seed(self, seed=None):
        self.np_random = np.random.RandomState(seed)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)

        if action != 26**2 * 2:
            action = bg_utils.to_bg_format(action, self.roll)
            self.game.execute_play(self.colors[self.agent_selection], action)

        winner = self.game.get_winner()
        if winner is not None:
            opp_agent = bg_utils.opp_agent(self, self.agent_selection)
            if winner == self.colors[self.agent_selection]:
                self.rewards[self.agent_selection] = 1
                self.rewards[opp_agent] = -1
            else:
                self.rewards[self.agent_selection] = -1
                self.rewards[opp_agent] = 1
            self.dones = {i: True for i in self.agents}
        else:
            self._clear_rewards()

        if self.double_roll == 0:
            self.agent_selection = self._agent_selector.next()

            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
            if roll[0] == roll[1]:
                self.double_roll = 2
            if(self.colors[self.agent_selection] == WHITE):
                roll = (-roll[0], -roll[1])
            self.roll = roll

        self._accumulate_rewards()

    def observe(self, agent):
        action_mask = np.zeros(1353, int)
        observation = np.array(self.game.get_board_features(agent), dtype=np.float32).reshape(198, )
        # only current agent can make legal moves
        if agent == self.agent_selection:
            valid_moves = bg_utils.get_valid_actions(self, self.roll)

            if self.double_roll > 0:
                self.handle_double_roll()
                valid_moves = bg_utils.double_roll(valid_moves)
                self.double_roll -= 1

            legal_moves = bg_utils.to_gym_format(valid_moves, self.roll)
            if len(legal_moves) == 0:
                legal_moves = [26**2 * 2]
        else:
            legal_moves = []

        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def reset(self):
        self.agents = self.possible_agents[:]
        self.dones = {i: False for i in self.agents}
        self.infos = {i: {'legal_moves': []} for i in self.agents}
        self._agent_order = list(self.agents)
        self._agent_selector.reinit(self._agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {i: 0 for i in self.agents}
        self.colors = {}
        self.double_roll = 0
        self.game = Game()

        opp_agent = bg_utils.opp_agent(self, self.agent_selection)

        roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
        while roll[0] == roll[1]:
            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
        if roll[0] > roll[1]:
            self.colors[self.agent_selection] = WHITE
            self.colors[opp_agent] = BLACK
            roll = (-roll[0], -roll[1])
        else:
            self.colors[self.agent_selection] = BLACK
            self.colors[opp_agent] = WHITE
        self.roll = roll

    def render(self, mode='human'):
        assert mode in ['human'], print(mode)
        if mode == 'human':
            self.game.render()
            return True

    def close(self):
        pass

    def handle_double_roll(self):
        if self.double_roll == 1:
            a = self._agent_order[0]
            self._agent_order[0] = self._agent_order[1]
            self._agent_order[1] = a
            self._agent_selector.reinit(self._agent_order)
            if self.agent_selection == self._agent_order[0]:
                self._agent_selector.next()
