'''
Frame stacking for flattened observations only
'''

from copy import deepcopy
import numpy as np
from gym.spaces import Box
from gamma_games.cooperative_pong.cooperative_pong import env as _env

from ray.rllib.env.multi_agent_env import MultiAgentEnv

class env(MultiAgentEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, stack_size = 4, *args):
        super(env, self).__init__()
        self.env = _env(*args)

        self.num_agents = self.env.num_agents
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.stack_size = stack_size
        self.action_space_dict = deepcopy(self.env.action_space_dict)
        new_obs_space_shape = (self.env.observation_space_dict[0].shape[0] * self.stack_size,)
        self.observation_space_dict = {agent_id : Box(low=0.0, high=1.0, shape=new_obs_space_shape, dtype=np.float32)\
                for agent_id in self.env.observation_space_dict.keys()}
        
        self.reset()
    
    def reset(self):
        obs_dict = self.env.reset()
        self.frame_stack = {agent_id : np.tile(obs_dict[agent_id], self.stack_size) \
                            for agent_id in obs_dict.keys()}
        # assumes all observations have the same size. All of them are flat.
        self.frame_len = np.random.choice([len(self.frame_stack[key]) \
                                           for key in self.frame_stack.keys()])
        return self.frame_stack

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

    def step(self, actions):

        observation_dict, reward_dict, done_dict, info_dict = self.env.step(actions)

        self.stack_obs(observation_dict)

        return self.frame_stack, reward_dict, done_dict, info_dict
    
    def stack_obs(self, new_obs_dict):
        '''
        Parameters
        ----------
        new_obs_dict : dictionary of observations
            Rearranges frame_stack. Appends the new observation ath the end.
            Throws away the oldest observation.            

        '''
        for agent_id in new_obs_dict.keys():
            self.frame_stack[agent_id][:self.frame_len-len(new_obs_dict[agent_id])] = \
                self.frame_stack[agent_id][len(new_obs_dict[agent_id]):]
            self.frame_stack[agent_id][self.frame_len-len(new_obs_dict[agent_id]):] = \
                new_obs_dict[agent_id]
