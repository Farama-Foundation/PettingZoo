from .pursuit_base import Pursuit as _env
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from pettingzoo.utils import AECEnv
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = list(range(self.num_agents))
        self.agent_order = self.agents[:]
        self.agent_selection = 0
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.0

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self):
        obs = self.env.reset()
        self.steps = 0
        return obs[0]

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

    def step(self, action, observe=True):
        if action == None or action == np.NaN:
            action = 4
        elif not self.action_spaces[self.agent_selection].contains(action):
            raise Exception('Action for agent {} must be in Discrete({}). \
                                It is currently {}'.format(self.agent_selection, self.action_spaces[self.agent_selection].n, action))
        obs = self.env.step(action, self.agent_selection)

        self.agent_selection = (self.agent_selection + 1) % self.num_agents
        self.steps += 1

        return obs

    def last_cycle(self):
        r, d, i = self.env.last_cycle(self.agent_selection)
        if self.steps >= 500:
            d = True
        return r, d, i

from .manual_test import manual_control
