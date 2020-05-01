import bg_utils
from pettingzoo import AECEnv
from pettingzoo.utils.env_logger import EnvLogger
from backgammon import Backgammon as Game, WHITE, BLACK, COLORS
from pettingzoo.utils import agent_selector
import gym.spaces as spaces
import numpy as np

class env(AECEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None):
        super(env, self).__init__()
        self.np_random = np.random.RandomState(seed)

        self.game = Game()
        self.seed = seed
        self.current_agent = None

        self.num_agents = 2
        self.agents = ["player_{}".format(i) for i in range(2)]

        self.action_spaces = {name: spaces.Box(low = np.float32(-2.0), high = np.float32(25.0), shape = (4,2), dtype = np.float32) for name in self.agents}

        self.agent_order = list(self.agents)
        self._agent_selector = agent_selector(self.agent_order)

        low = np.zeros((198, 1))
        high = np.ones((198, 1))

        for i in range(3, 97, 4):
            high[i] = 6.0
        high[96] = 7.5

        for i in range(101, 195, 4):
            high[i] = 6.0
        high[194] = 7.5

        self.observation_spaces = {i: spaces.Box(low=np.float32(low), high=np.float32(high), dtype=np.float32) for i in self.agents}
        self.counter = 0
        self.max_length_episode = 10000
        self.viewer = None

        self.has_reset = False
        self.has_rendered = False

    def step(self, action, observe = True):
        err_found = False

        # Check for invalid inputs
        backup_policy = "game terminating with no winner"

        if not self.has_reset:
            EnvLogger.error_step_before_reset()
            err_found = True
        act_space = self.action_spaces[self.agent_selection]
        if not err_found and np.any(np.isnan(action)):
            EnvLogger.warn_action_is_NaN(backup_policy)
            err_found = True
        if not err_found and not act_space.contains(action):
            action = np.array(action)
            if action.shape != act_space.shape:
                raise Exception("Action was an incorrect shape")
            EnvLogger.warn_action_out_of_bound(action,act_space,backup_policy)
            err_found = True
        if err_found:
            self.dones = {i: True for i in self.agents}
        elif not bg_utils.valid_action(self,action):
            EnvLogger.warn_on_illegal_move()
            self.dones = {i: True for i in self.agents}
            err_found = True

        #No errors
        elif not err_found:
            action = bg_utils.to_bg_format(action)
            self.game.execute_play(self.current_agent, action)

            winner = self.game.get_winner()

            if winner is not None or self.counter > self.max_length_episode:
                if winner == self.current_agent:
                    self.rewards[self.agent_selection] = 1
                else:
                    if(self.agent_selection == self.agents[0]):
                        self.rewards[self.agents[1]] = 1
                    else:
                        self.rewards[self.agents[0]] = 1

                self.dones = {i: True for i in self.agents}

            self.counter += 1

            self.agent_selection = self._agent_selector.next()
            self.current_agent = self.game.get_opponent(self.current_agent)

            #roll for the next turn
            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)

            if(self.current_agent == WHITE):
                roll = (-roll[0], -roll[1])

            legal_moves = np.array(bg_utils.to_gym_format(bg_utils.get_valid_actions(self,roll)))
            if len(legal_moves) == 0:
                legal_moves = [[[-2,-2],[-2,-2],[-2,-2],[-2,-2]]]
            self.infos = {i: {'legal_moves': legal_moves, 'roll':roll} for i in self.agents}

        if(observe == True):
            observation = self.observe(self.game.get_opponent(self.current_agent))
            return observation
        else:
            return

    def observe(self, agent):
        if not self.has_reset:
            EnvLogger.error_observe_before_reset()
        return np.array(self.game.get_board_features(agent)).reshape(198,1)

    def reset(self, observe=True):
        self.has_reset = True
        self.dones = {i: False for i in self.agents}

        self.agent_selection = self._agent_selector.reset()
        self.dones = {i: False for i in self.agents}
        self.rewards = {i: 0 for i in self.agents}

        # roll the dice
        roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)
        # roll the dice until they are different
        while roll[0] == roll[1]:
            roll = self.np_random.randint(1, 6), self.np_random.randint(1, 6)

        # set the current agent
        if roll[0] > roll[1]:
            self.current_agent = WHITE
            roll = (-roll[0], -roll[1])
        else:
            self.current_agent = BLACK

        self.game = Game()
        self.counter = 0

        self.infos = {i: {'legal_moves': np.array(bg_utils.to_gym_format(bg_utils.get_valid_actions(self, roll))), 'roll':roll} for i in self.agents}

        if observe:
            return self.observe(self.current_agent)
        else:
            return

    def render(self, mode='human'):
        assert mode in ['human'], print(mode)

        if not self.has_reset:
            EnvLogger.error_render_before_reset()

        if mode == 'human':
            self.game.render()
            return True

    def close(self):
        if not self.has_reset:
            EnvLogger.warn_close_before_reset()
        if not self.has_rendered:
             EnvLogger.warn_close_unrendered_env()
        self.has_rendered = False
