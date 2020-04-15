from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
from . import go
from . import coords
import numpy as np

class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, board_size : int = 19, komi: float = 7.5, **kwargs):
        # board_size: a int, representing the board size (board has a board_size x board_size shape)
        # komi: a float, representing points given to the second player.
        super(env, self).__init__()

        self._overwrite_go_global_variables(board_size = board_size)

        print(go.N)
        print(go.EMPTY_BOARD)

        self._komi = komi
        self._go = go.Position(komi = self._komi)

        self.agents = ['black', 'white']
        self.num_agents = len(self.agents)

        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.observation_spaces = self._convert_to_dict([spaces.Box(low=-1.0, high=1.0, shape=(self._N,self._N), dtype=np.int) for _ in range(self.num_agents)])
        self.action_spaces = self._convert_to_dict([spaces.Discrete(self._N*self._N+1) for _ in range(self.num_agents)])

        # obs, player_id = self.env.init_game()

        # self._last_obs = obs['obs']
        # self.agent_order = [self._int_to_name(agent) for agent in [player_id, 0 if player_id == 1 else 1]]
        # self._agent_selector = agent_selector(self.agent_order)
        # self.agent_selection = self._agent_selector.reset()
        # self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']

    def _overwrite_go_global_variables(self, board_size : int):
        self._N = board_size
        go.N = self._N
        go.ALL_COORDS = [(i, j) for i in range(self._N) for j in range(self._N)]
        go.EMPTY_BOARD = np.zeros([self._N, self._N], dtype=np.int8)
        go.NEIGHBORS = {(x, y): list(filter(self._check_bounds, [(x+1, y), (x-1, y), (x, y+1), (x, y-1)])) for x, y in go.ALL_COORDS}
        go.DIAGONALS = {(x, y): list(filter(self._check_bounds, [(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)])) for x, y in go.ALL_COORDS}
        return

    def _check_bounds(self, c):
        return 0 <= c[0] < self._N and 0 <= c[1] < self._N

    def _int_to_name(self, ind):
        return self.agents[ind]

    def _name_to_int(self, name):
        return self.agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    # def observe(self, agent):
    #     obs = self.env.get_state(self._name_to_int(agent))
    #     return obs['obs']

    # def step(self, action, observe=True):
    #     if self.dones[self.agent_selection]:
    #         self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
    #         obs = False
    #     else:
    #         if action not in self.infos[self.agent_selection]['legal_moves']:
    #             self.rewards[self.agent_selection] = -1
    #             self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
    #             info_copy = self.infos[self.agent_selection]
    #             self.infos = self._convert_to_dict([{'legal_moves': [2]} for agent in range(self.num_agents)])
    #             self.infos[self.agent_selection] = info_copy
    #             self.agent_selection = self._agent_selector.next()
    #             return self._last_obs
    #         obs, next_player_id = self.env.step(action)
    #         self._last_obs = obs['obs']
    #         if self.env.is_over():
    #             self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
    #             self.rewards = self._convert_to_dict(self.env.get_payoffs())
    #             self.infos[self._int_to_name(next_player_id)]['legal_moves'] = [2]
    #         else:
    #             self.infos[self._int_to_name(next_player_id)]['legal_moves'] = obs['legal_actions']
    #     self.agent_selection = self._agent_selector.next()
    #     if observe:
    #         return obs['obs'] if obs else self._last_obs

    # def reset(self, observe=True):
    #     obs, player_id = self.env.init_game()
    #     self.agent_order = [self._int_to_name(agent) for agent in [player_id, 0 if player_id == 1 else 1]]
    #     self._agent_selector.reinit(self.agent_order)
    #     self.agent_selection = self._agent_selector.reset()
    #     self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
    #     self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
    #     self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
    #     self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']
    #     self._last_obs = obs['obs']
    #     if observe:
    #         return obs['obs']
    #     else:
    #         return

    # def render(self, mode='human'):
    #     for player in self.agents:
    #         state = self.env.game.get_state(self._name_to_int(player))
    #         print("\n=============== {}'s Hand ===============".format(player))
    #         print_card(state['hand'])
    #         print("\n{}'s Chips: {}".format(player, state['my_chips']))
    #     print('\n================= Public Cards =================')
    #     print_card(state['public_cards']) if state['public_cards'] else print('No public cards.')
    #     print('\n')

    def close(self):
        pass
