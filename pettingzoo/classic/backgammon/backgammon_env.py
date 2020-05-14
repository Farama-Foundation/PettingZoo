from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from backgammon import Backgammon as Game, WHITE, BLACK, COLORS
from gym import spaces
import bg_utils
import numpy as np

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.NaNRandomWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

class raw_env(AECEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None):
        super().__init__()
        self.np_random = np.random.RandomState(seed)
        self.game = Game()

        self.current_agent = None
        self.num_agents = 2
        self.agents = ["player_{}".format(i) for i in range(2)]
        self.agent_order = list(self.agents)
        self._agent_selector = agent_selector(self.agent_order)

        self.action_spaces = {name: spaces.Discrete(26 * 26 * 2 + 1) for name in self.agents}

        low = np.zeros((198, 1))
        high = np.ones((198, 1))
        for i in range(3, 97, 4):
            high[i] = 6.0
        high[96] = 7.5
        for i in range(101, 195, 4):
            high[i] = 6.0
        high[194] = 7.5
        self.observation_spaces = {i: spaces.Box(low=np.float32(low), high=np.float32(high), dtype=np.float32) for i in self.agents}

        self.double_roll = 0
        self.has_reset = False
        self.has_rendered = False

    def step(self, action, observe = True):
        if action != 26**2 * 2:
            action = bg_utils.to_bg_format(action, self.roll)
            self.game.execute_play(self.current_agent, action)

        winner = self.game.get_winner()
        if winner is not None:
            if winner == self.current_agent:
                self.rewards[self.agent_selection] = 1
            else:
                if(self.agent_selection == self.agents[0]):
                    self.rewards[self.agents[1]] = 1
                else:
                    self.rewards[self.agents[0]] = 1
            self.dones = {i: True for i in self.agents}

        if self.double_roll == 0:
            self.agent_selection = self._agent_selector.next()
            self.current_agent = self.game.get_opponent(self.current_agent)

            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)

            if roll[0] == roll[1]:
                self.double_roll = 2
            if(self.current_agent == WHITE):
                roll = (-roll[0], -roll[1])
            self.roll = roll
        valid_moves = bg_utils.get_valid_actions(self,self.roll)

        if self.double_roll > 0:
            if self.double_roll == 1:
                prev_player = self.agent_selection
                next_player = self._agent_selector.next()
                prev_player_ind = self.agent_order.index(prev_player)
                curr_player_ind = self.agent_order.index(next_player)
                if prev_player_ind == self.num_agents - 1:
                    self.agent_order.remove(next_player)
                    self.agent_order.insert(0, next_player)
                else:
                    self.agent_order.remove(next_player)
                    if curr_player_ind < prev_player_ind:
                        self.agent_order.insert(0, self.agent_order.pop(-1))
                    self.agent_order.insert(self.agent_order.index(prev_player) + 1, next_player)
                skip_agent = prev_player_ind + 1
                self._agent_selector.reinit(self.agent_order)
                for _ in range(skip_agent+1):
                    self.agent_selection = self._agent_selector.next()

            valid_moves = bg_utils.double_roll(valid_moves)
            self.double_roll -= 1

        legal_moves = np.array(bg_utils.to_gym_format(valid_moves, self.roll))
        if len(legal_moves) == 0:
            legal_moves = [26**2 * 2]
        self.infos = {i: {'legal_moves': legal_moves} for i in self.agents}

        if(observe == True):
            observation = self.observe(self.game.get_opponent(self.current_agent))
            return observation

    def observe(self, agent):
        return np.array(self.game.get_board_features(agent)).reshape(198,1)

    def reset(self, observe=True):
        self.has_reset = True
        self.dones = {i: False for i in self.agents}
        self.agent_selection = self._agent_selector.reset()
        self.dones = {i: False for i in self.agents}
        self.rewards = {i: 0 for i in self.agents}

        roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
        while roll[0] == roll[1]:
            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
        if roll[0] > roll[1]:
            self.current_agent = WHITE
            roll = (-roll[0], -roll[1])
        else:
            self.current_agent = BLACK
        self.roll = roll
        self.game = Game()
        self.infos = {i: {'legal_moves': np.array(bg_utils.to_gym_format(bg_utils.get_valid_actions(self, roll), roll))} for i in self.agents}
        if observe:
            return self.observe(self.current_agent)

    def render(self, mode='human'):
        assert mode in ['human'], print(mode)
        if mode == 'human':
            self.game.render()
            return True

    def close(self):
        self.has_rendered = False
