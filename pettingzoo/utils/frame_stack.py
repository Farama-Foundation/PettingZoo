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
        obs_dim = obs_space_dict[agent_id].low.ndim
        # stack 1-D frames and 3-D frames
        if obs_dim == 1 or obs_dim == 3:
            new_shape = (stack_size,)
        # stack 2-D frames
        elif obs_dim == 2:
            new_shape = (stack_size, 1, 1)
        low = np.tile(obs_space.low, new_shape)
        high = np.tile(obs_space.high, new_shape)
        new_obs_space_dict[agent_id] = Box(low=low, high=high, dtype=dtype)
    return new_obs_space_dict


def stack_reset_obs(obs, stack_size):
    '''
    Input: 1 agent's observation only.
    Reset observations are only 1 obs. Tile them.
    '''
    # stack 1-D frames and 3-D frames
    if obs.ndim == 1 or obs.ndim == 3:
        new_shape = (stack_size,)
    # stack 2-D frames
    elif obs.ndim == 2:
        new_shape = (stack_size, 1, 1)
    frame_stack = np.tile(obs, new_shape)
    return frame_stack


def stack_obs(frame_stack, agent, obs, stack_size):
    '''
    Parameters
    ----------
    frame_stack : if not None, it is the stack of frames
    obs : new observation
        Rearranges frame_stack. Appends the new observation at the end.
        Throws away the oldest observation.
    stack_size : needed for stacking reset observations
    '''
    if frame_stack[agent] is None:
        frame_stack[agent] = stack_reset_obs(obs, stack_size)
    obs_shape = obs.shape
    agent_fs = frame_stack[agent]

    if len(obs_shape) == 1:
        agent_fs[:-obs_shape[-1]] = agent_fs[obs_shape[-1]:]
        agent_fs[-obs_shape[-1]:] = obs
    elif len(obs_shape) == 2:
        agent_fs[:-1] = agent_fs[1:]
        agent_fs[-1] = obs
    elif len(obs_shape) == 3:
        agent_fs[:, :, :-obs_shape[-1]] = agent_fs[:, :, obs_shape[-1]:]
        agent_fs[:, :, -obs_shape[-1]:] = obs
