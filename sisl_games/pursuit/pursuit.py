from .pursuit_base import Pursuit as _env
import numpy as np
import gym

from ray.rllib.env.multi_agent_env import MultiAgentEnv


def convert_to_dict(list_of_list):
    dict_of_list = {}
    for idx, i in enumerate(list_of_list):
        dict_of_list[idx] = i
    return dict_of_list


class env(MultiAgentEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, *args, **kwargs):
        super(env, self).__init__()
        self.env = _env(*args, **kwargs)

        self.num_agents = self.env.num_agents
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.n_act_agents = self.env.act_dims[0]
        self.action_space_dict = dict(zip(self.agent_ids, self.env.action_space))
        self.observation_space_dict = dict(zip(self.agent_ids, self.env.observation_space))
        self.steps = 0

        self.reset()

    def reset(self):
        obs = self.env.reset()
        self.steps = 0
        return convert_to_dict(obs)

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

    def step(self, action_dict):
        # unpack actions
        action_list = np.array([4 for _ in range(self.num_agents)])
        for i in self.agent_ids:
            if not self.action_space_dict[i].contains(action_dict[i]):
                raise Exception('Action for agent {} must be in Discrete({}). \
                                It is currently {}'.format(i, self.action_space_dict[i].n, action_dict[i]))
            action_list[i] = action_dict[i]

        observation, reward, done, info = self.env.step(action_list)

        if self.steps >= 500:
            done = [True]*self.num_agents

        observation_dict = convert_to_dict(observation)
        reward_dict = convert_to_dict(reward)
        info_dict = convert_to_dict(info)
        done_dict = convert_to_dict(done)
        done_dict["__all__"] = done[0]

        self.steps += 1

        return observation_dict, reward_dict, done_dict, info_dict
