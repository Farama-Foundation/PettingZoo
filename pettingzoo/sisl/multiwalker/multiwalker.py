from .multiwalker_base import MultiWalkerEnv as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import EnvLogger
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=0, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(seed, *args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = ["walker_" + str(r) for r in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.04
        self.observations = self.env.get_last_obs()

        self.has_reset = False

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        self.has_reset = True
        self.env.reset()
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

    def observe(self, agent):
        if not self.has_reset:
            EnvLogger.error_observe_before_reset()
        return self.env.observe(self.agent_name_mapping[agent])

    def step(self, action, observe=True):
        if not self.has_reset:
            EnvLogger.error_step_before_reset()
        agent = self.agent_selection
        if action is None or any(np.isnan(action)):
            EnvLogger.warn_action_is_NaN(backup_policy="setting to zeros")
            action = np.zeros_like(self.action_spaces[agent].sample())
        elif not self.action_spaces[agent].contains(action):
            EnvLogger.warn_action_out_of_bound(action=action, action_space=self.action_spaces[agent], backup_policy="setting to zeros")
            action = np.zeros_like(self.action_spaces[agent].sample())
        action = np.array(action, dtype=np.float32)
        self.env.step(action, self.agent_name_mapping[agent], self._agent_selector.is_last())
        for r in self.rewards:
            self.rewards[r] = self.env.get_last_rewards()[self.agent_name_mapping[r]]
        for d in self.dones:
            self.dones[d] = self.env.get_last_dones()[self.agent_name_mapping[r]]
        self.agent_selection = self._agent_selector.next()

        if self.env.frames >= self.env.max_frames:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        self.steps += 1
        if observe:
            return self.observe(self.agent_selection)
