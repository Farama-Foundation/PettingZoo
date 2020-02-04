from .waterworld_base import MAWaterWorld as _env
import numpy as np

from ray.rllib.env.multi_agent_env import MultiAgentEnv


class env(MultiAgentEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.action_space_dict = dict(zip(self.agent_ids, self.env.action_space))
        self.observation_space_dict = dict(zip(self.agent_ids, self.env.observation_space))

        self.reset()

    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agent_ids, list_of_list))

    def reset(self):
        observation = self.env.reset()
        return self.convert_to_dict(observation)

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

    def step(self, action_dict):
        # unpack actions
        actions = [0.0 for _ in range(len(action_dict))]
        for key in action_dict.keys():
            actions[key] = action_dict[key]

        observation, reward, done, info = self.env.step(actions)

        observation_dict = self.convert_to_dict(observation)
        reward_dict = self.convert_to_dict(reward)
        info_dict = self.convert_to_dict(info)
        done_dict = self.convert_to_dict(done)
        done_dict["__all__"] = done[0]

        return observation_dict, reward_dict, done_dict, info_dict
