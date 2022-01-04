import numpy as np
from gym.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .multiwalker_base import MultiWalkerEnv as _env

"""
In this environment, bipedal robots attempt to carry a package as far right as possible. A package is placed on top of 3 (by default) bipedal robots which you control. A positive reward is awarded to each walker, which is the change in the package distance summed with 130 times the change in the walker's position. By default, the environment is done if any walker or the package falls. A walker is given a reward of -100 when they fail the game by either condition. If the walker falls, they are penalized an additional -10. If the `terminate_on_fall` setting is set to false, the game continues until the package falls. If the `remove_on_fall` setting is set to True, the walkers are removed from the scene after they fall. If the global reward mechanic is chosen, the mean of all rewards is given to each agent. Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 31 element vector containing simulated noisy lidar data about the environment and information about neighboring walkers. The environment's duration is capped at 500 frames by default (can be controlled by the `max_cycles` setting).

### Observation Space

Each agent receives an observation composed of various physical properties of its legs and joints, as well as LIDAR readings from the space immediately in front and below the robot. The observation also includes information about neighboring walkers, and the package, which have normally distributed signal noise controlled by `position_noise` and `angle_noise`. For walkers without neighbors, observations about neighbor positions are zero.

This table enumerates the observation space:


### Arguments
:param n_walkers:  number of bipedal walker agents in environment
:param position_noise:  noise applied to agent positional sensor observations
:param angle_noise:  noise applied to agent rotational sensor observations
:param local_ratio: Proportion of reward allocated locally vs distributed among all agents
:param forward_reward:  reward applied for an agent standing, scaled by agent's x coordinate
:param fall_reward:  reward applied when an agent falls down
:param terminate_reward: reward applied to a walker for failing the environment
:param terminate_on_fall: toggles whether agent is done if it falls down
:param remove_on_fall: Remove walker when it falls (only does anything when `terminate_on_fall` is False)
:param max_cycles:  after max_cycles steps all agents will return done
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    metadata = {'render.modes': ['human', "rgb_array"], 'name': 'multiwalker_v7'}

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
