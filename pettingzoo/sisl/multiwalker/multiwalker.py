import numpy as np
from gym.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .multiwalker_base import FPS
from .multiwalker_base import MultiWalkerEnv as _env


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    metadata = {
        'render.modes': ['human', "rgb_array"],
        'name': 'multiwalker_v8',
        'is_parallelizable': True,
        'video.frames_per_second': FPS,
    }

    def __init__(self, *args, **kwargs):
        EzPickle.__init__(self, *args, **kwargs)
        self.env = _env(*args, **kwargs)

        self.agents = ["walker_" + str(r) for r in range(self.env.num_agents)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.num_agents))))
        self._agent_selector = agent_selector(self.agents)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(
            zip(self.agents, self.env.observation_space))
        self.steps = 0

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        self.env.seed(seed)

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self):
        self.env.reset()
        self.steps = 0
        self.agents = self.possible_agents[:]
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self._cumulative_rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.rewards = dict(zip(self.agents, [(0) for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render(mode)

        import pyglet
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_data = buffer.get_image_data()
        arr = np.fromstring(image_data.get_data(), dtype=np.uint8, sep='')
        arr = arr.reshape(buffer.height, buffer.width, 4)
        arr = arr[::-1, :, 0:3]
        return arr if mode == "rgb_array" else None

    def observe(self, agent):
        return self.env.observe(self.agent_name_mapping[agent])

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection
        action = np.array(action, dtype=np.float32)
        is_last = self._agent_selector.is_last()
        self.env.step(action, self.agent_name_mapping[agent], is_last)
        if is_last:
            last_rewards = self.env.get_last_rewards()
            for r in self.rewards:
                self.rewards[r] = last_rewards[self.agent_name_mapping[r]]
            for d in self.dones:
                self.dones[d] = self.env.get_last_dones()[self.agent_name_mapping[d]]
            self.agent_name_mapping = {agent: i for i, (agent, done) in enumerate(zip(self.possible_agents, self.env.get_last_dones()))}
            iter_agents = self.agents[:]
            for a, d in self.dones.items():
                if d:
                    iter_agents.remove(a)
            self._agent_selector.reinit(iter_agents)
        else:
            self._clear_rewards()
        if self._agent_selector.agent_order:
            self.agent_selection = self._agent_selector.next()

        if self.env.frames >= self.env.max_cycles:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()
        self._dones_step_first()
        self.steps += 1
