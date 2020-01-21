#!/usr/bin/env python3

from .cooperative_pong_gym import env as _env 
import numpy as np

from ray.rllib.env.multi_agent_env import MultiAgentEnv

def convert_to_dict(list_of_list):
    dict_of_list = {}
    for idx, i in enumerate(list_of_list):
        dict_of_list[idx] = i
    return dict_of_list

class env(MultiAgentEnv):
    
    metadata = {'render.modes': ['human']}	
		
    def __init__(self, *args):
        super(env, self).__init__()
        self.env = _env(*args)
        
        self.num_agents = 2
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.action_space_dict = dict(zip(self.agent_ids, [self.env.action_space[0]]*self.num_agents))
        self.observation_space_dict = dict(zip(self.agent_ids, [self.env.observation_space[0]]*self.num_agents))
        
        self.reset()
        
    def reset(self):
        self.env.reset()
        return self.observe()
    
    def close(self):
        self.env.close()
    
    def render(self):
        self.env.render()
    
    def observe(self):
        obs = self.env.observe()
        return convert_to_dict(obs)

    def step(self, action_dict):
        # unpack actions
        actions = []
        for idx, agent in enumerate(self.agent_ids):
            dist = action_dict[agent]
            normDist = dist/np.sum(dist)
            normDist = np.concatenate(([0], normDist))
            normDist = np.cumsum(normDist)
            cut = np.random.rand()
            for action in range(len(normDist)-1):
                if cut >= normDist[action] and cut < normDist[action+1]:
                    break
            actions.append(action)
        
        observation, reward, done, info = self.env.step(actions)

        observation_dict = convert_to_dict(observation)
        reward_dict = convert_to_dict(reward)
        info_dict = convert_to_dict(info)
        done_dict = convert_to_dict(done)
        done_dict["__all__"] = done[0]
        
        return observation_dict, reward_dict, done_dict, info_dict
