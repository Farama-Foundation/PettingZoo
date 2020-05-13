from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
from rlcard.utils.utils import print_card
import numpy as np
from pettingzoo.utils import wrappers


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
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        self.env = rlcard.make('limit-holdem', config={"seed": seed},)
        self.agents = ['player_0', 'player_1']
        self.num_agents = len(self.agents)
        self.has_reset = False

        self.observation_spaces = self._convert_to_dict([spaces.Box(low=0.0, high=1.0, shape=(72,), dtype=np.bool) for _ in range(self.num_agents)])
        self.action_spaces = self._convert_to_dict([spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)])

        self.agent_order = self.agents
        self._agent_selector = agent_selector(self.agent_order)

    def _int_to_name(self, ind):
        return self.agents[ind]

    def _name_to_int(self, name):
        return self.agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        return obs['obs']

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        self._last_obs = obs['obs']
        if self.env.is_over():
            self.dones = self._convert_to_dict([True for _ in range(self.num_agents)])
            self.rewards = self._convert_to_dict(self.env.get_payoffs())
            self.infos[self._int_to_name(next_player_id)]['legal_moves'] = [2]
        else:
            self.infos[self._int_to_name(next_player_id)]['legal_moves'] = obs['legal_actions']
        self.agent_selection = self._agent_selector.next()
        if observe:
            return obs['obs'] if obs else self._last_obs

    def reset(self, observe=True):
        self.has_reset = True
        obs, player_id = self.env.reset()
        self.agent_order = [self._int_to_name(agent) for agent in [player_id, 0 if player_id == 1 else 1]]
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self._convert_to_dict(np.array([0.0, 0.0]))
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']
        self._last_obs = obs['obs']
        if observe:
            return obs['obs']
        else:
            return

    def render(self, mode='human'):
        for player in self.agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print("\n=============== {}'s Hand ===============".format(player))
            print_card(state['hand'])
            print("\n{}'s Chips: {}".format(player, state['my_chips']))
        print('\n================= Public Cards =================')
        print_card(state['public_cards']) if state['public_cards'] else print('No public cards.')
        print('\n')

    def close(self):
        pass
