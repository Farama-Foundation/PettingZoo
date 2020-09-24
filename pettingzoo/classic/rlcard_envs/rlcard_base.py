from pettingzoo import AECEnv
from gym import spaces
import rlcard
import random
import numpy as np
from pettingzoo.utils import wrappers


class RLCardBase(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, name, num_players, obs_shape):
        super().__init__()
        self.name = name
        self.env = rlcard.make(name)
        if not hasattr(self, "agents"):
            self.agents = [f'player_{i}' for i in range(num_players)]
        self.num_agents = len(self.agents)

        dtype = self.env.reset()[0]['obs'].dtype
        if dtype == np.dtype(np.int64):
            self._dtype = np.dtype(np.int8)
        elif dtype == np.dtype(np.float64):
            self._dtype = np.dtype(np.float32)
        else:
            self._dtype = dtype

        self.observation_spaces = self._convert_to_dict([spaces.Box(low=0.0, high=1.0, shape=obs_shape, dtype=self._dtype) for _ in range(self.num_agents)])
        self.action_spaces = self._convert_to_dict([spaces.Discrete(self.env.game.get_action_num()) for _ in range(self.num_agents)])

    def seed(self, seed=None):
        self.env = rlcard.make(self.name, config={"seed": seed})

    def _scale_rewards(self, reward):
        return reward

    def _int_to_name(self, ind):
        return self.agents[ind]

    def _name_to_int(self, name):
        return self.agents.index(name)

    def _convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        return obs['obs'].astype(self._dtype)

    def step(self, action, observe=True):
        obs, next_player_id = self.env.step(action)
        next_player = self._int_to_name(next_player_id)
        self._last_obs = obs['obs']
        if self.env.is_over():
            self.rewards = self._convert_to_dict(self._scale_rewards(self.env.get_payoffs()))
            self.infos[next_player]['legal_moves'] = []
            self.dones = self._convert_to_dict([True if self.env.is_over() else False for _ in range(self.num_agents)])
        else:
            self.infos[next_player]['legal_moves'] = obs['legal_actions']
        self.agent_selection = next_player
        if observe:
            return obs['obs'].astype(self._dtype) if obs else self._last_obs.astype(self._dtype)

    def reset(self, observe=True):
        obs, player_id = self.env.reset()
        self.agent_selection = self._int_to_name(player_id)
        self.rewards = self._convert_to_dict([0 for _ in range(self.num_agents)])
        self.dones = self._convert_to_dict([False for _ in range(self.num_agents)])
        self.infos = self._convert_to_dict([{'legal_moves': []} for _ in range(self.num_agents)])
        self.infos[self._int_to_name(player_id)]['legal_moves'] = obs['legal_actions']
        self._last_obs = obs['obs']
        if observe:
            return obs['obs'].astype(self._dtype)
        else:
            return

    def render(self, mode='human'):
        raise NotImplementedError()

    def close(self):
        pass
