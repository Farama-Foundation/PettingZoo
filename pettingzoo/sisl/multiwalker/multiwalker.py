from .multiwalker_base import MultiWalkerEnv as _env
from pettingzoo.utils import AECEnv, agent_selector
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = list(range(self.num_agents))
        self.agent_selection = 0
        self.agent_order = self.agents[:]
        self._agent_selector_object = agent_selector(self.agent_order)
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.04

        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [None for _ in self.agents]))
        self.observations = self.env.get_last_obs()

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self, observe=True):
        observation = self.env.reset()
        self.steps = 0
        self.agent_selection = 0
        self._agent_selector_object.reinit(self.agent_order)
        if observe:
            return observation

    def close(self):
        self.env.close()

    def render(self, mode="human"):
        self.env.render()

    def observe(self, agent):
        agent = agent % self.num_agents
        return self.observations[agent]

    # def step(self, action_dict):
    #     # unpack actions
    #     actions = [0.0 for _ in range(len(action_dict))]

    #     for agent_id in self.agents:
    #         if any(np.isnan(action_dict[agent_id])):
    #             action_dict[agent_id] = [0 for _ in action_dict[agent_id]]
    #         elif not self.action_spaces[agent_id].contains(action_dict[agent_id]):
    #             raise Exception('Action for agent {} must be in {}. \
    #                             It is currently {}'.format(agent_id, self.action_spaces[agent_id], action_dict[agent_id]))
    #         actions[agent_id] = action_dict[agent_id]

    #     observation, reward, done, info = self.env.step(actions)

    #     if self.steps >= 500:
    #         done = [True]*self.num_agents

    #     observation_dict = self.convert_to_dict(observation)
    #     reward_dict = self.convert_to_dict(reward)
    #     info_dict = self.convert_to_dict(info)
    #     done_dict = self.convert_to_dict(done)
    #     done_dict["__all__"] = done[0]

    #     self.steps += 1

    #     return observation_dict, reward_dict, done_dict, info_dict

    def step(self, action, observe=True):
        self.agent_selection = self._agent_selector_object.select()
        action = np.array(action, dtype=np.float32)
        if any(np.isnan(action)):
            action = [0 for _ in action]
        elif not self.action_spaces[self.agent_selection].contains(action):
            raise Exception('Action for agent {} must be in {}. It is currently {}'.format(self.agent_selection, self.action_spaces[self.agent_selection], action))

        self.env.step(action, self.agent_selection, self._agent_selector_object.is_last())
        self.rewards = self.env.get_last_rewards()
        self.dones = self.env.get_last_dones()
        self.observations = self.env.get_last_obs()

        if self.steps >= 500:
            self.dones = dict(zip(self.agents, [True for _ in self.agents]))
        

        self.steps += 1
        return self.observe(self.agent_selection+1)
