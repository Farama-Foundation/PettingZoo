'''
Frame stacking for heterogeneous observation spaces. Each agent can have a different Box observation space.
'''

import numpy as np
from gym.spaces import Box

def stack_obs_space(obs_space_dict, stack_size):
    '''
    obs_space_dict: Dictionary of observations spaces of agents
    stack_size: Number of frames in the observation stack
    Returns:
        New obs_space_dict
    '''
    assert isinstance(obs_space_dict, dict), "obs_space_dict is not a dictionary."

    new_obs_space_dict = {}

    for key in obs_space_dict.keys():
        obs_space = obs_space_dict[key]
        assert isinstance(obs_space, Box), "Stacking is currently only allowed for Box obs space. The given obs space is {}".format(obs_space)
        dtype = obs_space.dtype
        low = np.tile(obs_space.low, stack_size)
        high = np.tile(obs_space.high, stack_size)
        new_obs_space_dict[key] = Box(low=low, high=high, dtype=dtype)
    return new_obs_space_dict

def stack_reset_obs(obs_dict, stack_size):
    '''
    Reset observations are only 1 obs per agent. Tile them.
    '''
    frame_stack = {agent_id: np.tile(obs_dict[agent_id], stack_size) for agent_id in obs_dict.keys()}
    return frame_stack

def stack_obs(frame_stack, new_obs_dict):
    '''
    Parameters
    ----------
    obs_dict : dictionary of observations
        Rearranges frame_stack. Appends the new observation at the end.
        Throws away the oldest observation.
    '''
    for agent_id in new_obs_dict.keys():
        new_obs = new_obs_dict[agent_id]
        last_axis_len = new_obs.shape[-1]

        # stack frames in 1-D
        if len(obs_shape) == 1:
            frame_stack[agent_id][:-last_axis_len] = frame_stack[agent_id][last_axis_len:]
            frame_stack[agent_id][-last_axis_len:] = new_obs

        # stack frames in 2-D
        elif len(obs_shape) == 2:
            frame_stack[agent_id][:, :-last_axis_len] = frame_stack[agent_id][:, last_axis_len:]
            frame_stack[agent_id][:, -last_axis_len:] = new_obs

        # stack frames in 3-D
        elif len(obs_shape) == 3:
            frame_stack[agent_id][:, :, :-last_axis_len] = frame_stack[agent_id][:, :, last_axis_len:]
            frame_stack[agent_id][:, :, -last_axis_len:] = new_obs
    # return frame_stack
    # frame_stack itself changes

"""
from copy import deepcopy
class env(MultiAgentEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, stack_size=4, *args):
        super(env, self).__init__()
        self.env = _env(*args)

        self.num_agents = self.env.num_agents
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.stack_size = stack_size
        self.action_space_dict = deepcopy(self.env.action_space_dict)
        new_obs_space_shape = (self.env.observation_space_dict[0].shape[0] * self.stack_size,)
        self.observation_space_dict = {agent_id: Box(low=0.0, high=1.0, shape=new_obs_space_shape, dtype=np.float32)
                                       for agent_id in self.env.observation_space_dict.keys()}

        self.reset()

    def reset(self):
        obs_dict = self.env.reset()
        self.frame_stack = {agent_id: np.tile(obs_dict[agent_id], self.stack_size)
                            for agent_id in obs_dict.keys()}
        # assumes all observations have the same size. All of them are flat.
        self.frame_len = np.random.choice([len(self.frame_stack[key])
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
"""
