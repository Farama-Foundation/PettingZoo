#!/usr/bin/env python3

from .waterworld_base import MAWaterWorld as _env 
import numpy as np

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
        self.action_space_dict = dict(zip(self.agent_ids, self.env.action_space))
        self.observation_space_dict = dict(zip(self.agent_ids, self.env.observation_space))
        
        self.reset()
        
    def reset(self):
        observation = self.env.reset()
        observation_dict = convert_to_dict(observation)
        return observation_dict
    
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

        observation_dict = convert_to_dict(observation)
        reward_dict = convert_to_dict(reward)
        info_dict = convert_to_dict(info)
        done_dict = convert_to_dict(done)
        done_dict["__all__"] = done[0]
        
        return observation_dict, reward_dict, done_dict, info_dict
