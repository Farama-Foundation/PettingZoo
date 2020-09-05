from .multiwalker_base import MultiWalkerEnv as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import numpy as np
from gym.utils import EzPickle
from pettingzoo.utils import wrappers
from pettingzoo.utils.to_parallel import parallel_wrapper_fn


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.NanZerosWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = ["walker_" + str(r) for r in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.04
        self.observations = self.env.get_last_obs()

        self.has_reset = False

    def seed(self, seed=None):
        self.env.seed(seed)

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        self.has_reset = True
        self.env.reset()
        self.steps = 0
        self._agent_selector.reinit(self.agents)
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
        return self.env.observe(self.agent_name_mapping[agent])

    def step(self, action, observe=True):
        agent = self.agent_selection
        action = np.array(action, dtype=np.float32)
        self.env.step(action, self.agent_name_mapping[agent], self._agent_selector.is_last())
        for r in self.rewards:
            self.rewards[r] = self.env.get_last_rewards()[self.agent_name_mapping[r]]
        for d in self.dones:
            self.dones[d] = self.env.get_last_dones()[self.agent_name_mapping[d]]
        self.agent_selection = self._agent_selector.next()

        if self.env.frames >= self.env.max_frames:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        self.steps += 1
        if observe:
            return self.observe(self.agent_selection)
