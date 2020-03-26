from .pursuit_base import Pursuit as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = ["pursuer_"+str(a) for a in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.agent_order = self.agents[:]
        self.agent_selector_obj = agent_selector(self.agent_order)
        self.agent_selection = 0
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.0

        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

        self.reset()

    def reset(self, observe=True):
        self.steps = 0
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.agent_selector_obj.reinit(self.agent_order)
        self.agent_selection = self.agent_selector_obj.next()
        if observe:
            return self.observe(self.agent_selection)

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def step(self, action, observe=True):
        if not np.isscalar(action):
            action = action[0]

        agent = self.agent_selection
        if action is None or action == np.NaN:
            action = 4
        elif not self.action_spaces[agent].contains(action):
            raise Exception('Action for agent {} must be in Discrete({}). \
                                It is currently {}'.format(agent, self.action_spaces[agent].n, action))
        self.env.step(action, self.agent_name_mapping[agent], self.agent_selector_obj.is_last())
        for k in self.dones:
            if self.env.frames >= self.env.max_frames:
                self.dones[k] = True
            else:
                self.dones[k] = self.env.is_terminal
        for k in self.agents:
            self.rewards[k] = self.env.latest_reward_state[self.agent_name_mapping[k]]
        self.steps += 1
        self.agent_selection = self.agent_selector_obj.next()
        if observe:
            return self.observe(self.agent_selection)

    def observe(self, agent):
        o = np.array(self.env.safely_observe(self.agent_name_mapping[agent]))
        return o


from .manual_control import manual_control
