from .pursuit_base import Pursuit as _env
from pettingzoo.utils import AECEnv, agent_selector
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = list(range(self.num_agents))
        self.agent_order = self.agents[:]
        self.agent_selector_obj = agent_selector(self.agent_order)
        self.agent_selection = 0
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.0

        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [None for _ in self.agents]))

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        obs = self.env.reset()
        self.steps = 0
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [None for _ in self.agents]))
        self.agent_selector_obj.reinit(self.agent_order)
        if observe:
            return obs[0]

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def step(self, action, observe=True):
        self.agent_selection = self.agent_selector_obj.select()
        if action == None or action == np.NaN:
            action = 4
        elif not self.action_spaces[self.agent_selection].contains(action):
            raise Exception('Action for agent {} must be in Discrete({}). \
                                It is currently {}'.format(self.agent_selection, self.action_spaces[self.agent_selection].n, action))
        obs = self.env.step(action, self.agent_selection, self.agent_selector_obj.is_last())

        self.steps += 1

        return self.observe(self.agent_selection+1)

    def observe(self, agent):
        agent = agent % self.num_agents
        return self.env.latest_obs[agent]


from .manual_test import manual_control
