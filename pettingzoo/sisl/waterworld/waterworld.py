from .waterworld_base import MAWaterWorld as _env
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from pettingzoo.utils import AECEnv
import numpy as np


class env(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agents = list(range(self.num_agents))
        self.agent_selection = 0
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.steps = 0
        self.display_wait = 0.03

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agents, list_of_list))

    def reset(self):
        observation = self.env.reset()
        self.steps = 0
        return observation

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

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

    def last_cycle(self):
        r,d,i = self.env.last_cycle(self.agent_selection)
        if self.steps >= 500:
            d = True
        return r,d,i

    def step(self, action, observation = True):
        if any(action) == None or any(action) == np.NaN:
            action = [0 for _ in action]
        elif not self.action_spaces[self.agent_selection].contains(action):
            raise Exception('Action for agent {} must be in {}. \
                                 It is currently {}'.format(self.agent_selection, self.action_spaces[self.agent_selection], action))

        obs= self.env.step(action, self.agent_selection)
        
        self.steps += 1

        self.agent_selection = (self.agent_selection + 1) % self.num_agents
        return obs