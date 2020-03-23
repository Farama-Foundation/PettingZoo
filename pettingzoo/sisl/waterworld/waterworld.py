from .waterworld_base import MAWaterWorld as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
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
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.03

        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        observation = self.env.reset()
        self.steps = 0
        self.agent_selector_obj.reinit(self.agent_order)
        self.agent_selection = self.agent_selector_obj.next()
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        if observe:
            return self.observe(0)

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def step(self, action, observe=True):
        agent = self.agent_selection
        if any(action) == None or any(action) == np.NaN:
            action = [0 for _ in action]
        elif not self.action_spaces[agent].contains(action):
            raise Exception('Action for agent {} must be in {}. \
                                 It is currently {}'.format(agent, self.action_spaces[agent], action))

        self.env.step(action, agent, self.agent_selector_obj.is_last())
        self.rewards[agent] = self.env.last_rewards[agent]

        if self.env.frames >= self.env.max_frames:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))
        else:
            self.dones = dict(zip(self.agents, self.env.last_dones))
        self.agent_selection = self.agent_selector_obj.next()

        # AGENT SELECT

        self.steps += 1

        if observe:
            return self.observe(self.agent_selection)

    def observe(self, agent):
        agent = agent % self.num_agents
        return self.env.observe(agent)
