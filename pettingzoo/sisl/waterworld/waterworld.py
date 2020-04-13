from .waterworld_base import MAWaterWorld as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import EnvLogger
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = ["pursuer_" + str(r) for r in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
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
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        self.steps = 0
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        if observe:
            return self.observe(self.agent_selection)

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def step(self, action, observe=True):
        agent = self.agent_selection
        if action is None or any(action) is None or any(action) == np.NaN:
            EnvLogger.warn_action_out_of_bound()
            raise Exception("Action for agent {} cannot be null".format(agent))
        elif not self.action_spaces[agent].contains(action):
            EnvLogger.warn_action_out_of_bound()
            raise Exception('Action for agent {} must be in {}. \
                                 It is currently {}'.format(agent, self.action_spaces[agent], action))

        self.env.step(action, self.agent_name_mapping[agent], self._agent_selector.is_last())
        for r in self.rewards:
            self.rewards[r] = self.env.last_rewards[self.agent_name_mapping[r]]

        if self.env.frames >= self.env.max_frames:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))
        else:
            self.dones = dict(zip(self.agents, self.env.last_dones))
        self.agent_selection = self._agent_selector.next()

        # AGENT SELECT

        self.steps += 1

        if observe:
            return self.observe(self.agent_selection)

    def observe(self, agent):
        return self.env.observe(self.agent_name_mapping[agent])
