from .waterworld_base import MAWaterWorld as _env
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
import numpy as np


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.NanZerosWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, seed=None, *args, **kwargs):
        super().__init__()
        self.env = _env(seed, *args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = ["pursuer_" + str(r) for r in range(self.num_agents)]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.03
        self.has_reset = False

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        self.has_reset = True
        self.steps = 0
        self.env.reset()
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = dict(
            zip(self.agents, [np.float64(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        if observe:
            return self.observe(self.agent_selection)

    def close(self):
        if self.has_reset:
            self.env.close()

    def render(self, mode="human"):
        return self.env.render()

        # import pyglet
        # buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        # image_data = buffer.get_image_data()
        # arr = np.fromstring(image_data.get_data(), dtype=np.uint8, sep='')
        # arr = arr.reshape(buffer.height, buffer.width, 4)
        # arr = arr[::-1, :, 0:3]
        # return arr

    def step(self, action, observe=True):
        agent = self.agent_selection

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
