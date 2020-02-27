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

    for agent_id in obs_space_dict.keys():
        obs_space = obs_space_dict[agent_id]
        assert isinstance(obs_space, Box), "Stacking is currently only allowed for Box obs space. The given obs space is {}".format(obs_space)
        dtype = obs_space.dtype
        obs_shape = obs_space_dict[agent_id].shape
        # stack 1-D frames
        if len(obs_shape) == 1:
            shape = (stack_size, 1)
        elif len(obs_shape) == 2:
            shape = (stack_size, 1, 1)
        elif len(obs_shape) == 3:
            shape = (stack_size, 1, 1, 1)
        low = np.tile(obs_space.low, shape)
        high = np.tile(obs_space.high, shape)
        new_obs_space_dict[agent_id] = Box(low=low, high=high, dtype=dtype)
    return new_obs_space_dict

def stack_reset_obs(obs_dict, stack_size):
    '''
    Reset observations are only 1 obs per agent. Tile them.
    '''
    frame_stack = {}
    for agent_id in obs_dict.keys():
        obs_shape = obs_dict[agent_id].shape
        # stack 1-D frames
        if len(obs_shape) == 1:
            shape = (stack_size, 1)
        elif len(obs_shape) == 2:
            shape = (stack_size, 1, 1)
        elif len(obs_shape) == 3:
            shape = (stack_size, 1, 1, 1)
        frame_stack[agent_id] =  np.tile(obs_dict[agent_id], shape)
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
        frame_stack[agent_id][:-1] = frame_stack[agent_id][1:]
        frame_stack[agent_id][-1] = new_obs
