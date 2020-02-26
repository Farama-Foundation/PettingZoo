import numpy as np
from gym.spaces import Box
from warnings import warn
from skimage import measure
from ray.rllib.env.multi_agent_env import MultiAgentEnv

from .frame_stack import stack_obs_space, stack_reset_obs, stack_obs

COLOR_RED_LIST = ["full", 'R', 'G', 'B']
OBS_RESHAPE_LIST = ["expand", "flatten"]


class wrapper(MultiAgentEnv):
    
    def __init__(self, env, color_reduction=None, down_scale=None, reshape=None, range_scale=None, new_dtype=None, frame_stacking=1):
        '''
        Creates a wrapper around `env`.

        Parameters
        ----------
        env : TYPE
            DESCRIPTION.
        color_reduction : str or dict, optional
            True grayscale or reduce color to one channel. The default is None.
        down_scale : tuple or dict, optional
            Downscale observations using a filter. The default is None.
        reshape : str, optional
            Reshape observations: "expand" or "flatten". The default is None.
        range_scale : tuple or dict, optional
            new_obs = obs/(max_obs-min_obs) - min_obs. The default is None.
        new_dtype : type or dict, optional
            New dtype for observations. The default is None.
        frame_stacking : int, optional
            No. of observation frames to stack.. The default is 1.

        Returns
        -------
        None.

        '''
        self.env = env
        self.color_reduction = color_reduction
        self.down_scale = down_scale
        self.reshape = reshape
        self.range_scale = range_scale
        self.new_dtype = new_dtype
        self.frame_stacking = frame_stacking
        
        self.agents = self.env.agents
        self.num_agents = len(self.agents)
        self.observation_spaces = self.env.observation_spaces
        self.action_spaces = self.env.action_spaces
        
        if self.frame_stacking > 1:
            self.stack_of_frames = {}
        
        self._check_wrapper_params()
        
        if self._check_box_space():
            self.modify_observation_space()
        else:
            warn("All agents' observation spaces are not Box: {}, and as such the observation spaces are not modified.".format(self.observation_spaces))
        
    def _check_wrapper_params(self):
        '''
        Checks if valid parameters are passed to wrapper object.

        Returns
        -------
        None.

        '''
        if self.color_reduction is not None:
            assert isinstance(self.color_reduction, str) or isinstance(self.color_reduction, dict), "color_reduction must be str or dict. It is {}".format(self.color_reduction)
            if isinstance(self.color_reduction, str):
                self.color_reduction = dict(zip(self.agents, [self.color_reduction for _ in enumerate(self.agents)]))            
            if isinstance(self.color_reduction, dict):
                for agent in self.agents:
                    assert agent in self.color_reduction.keys(), "Agent id {} is not a key of color_reduction {}".format(agent, self.color_reduction)
                    assert self.color_reduction[agent] in COLOR_RED_LIST, "color_reduction must be in {}".format(COLOR_RED_LIST)
                    assert len(self.observation_spaces[agent].low.shape) == 3, "To apply color_reduction, length of shape of obs space of the agent should be 3. It is {}".format(len(self.observation_spaces[agent].low.shape))
                    if self.color_reduction[agent] == "full":
                        warn("You have chosen true grayscaling. It might be too slow. Choose a specific channel for better performance")

        if self.down_scale is not None:
            assert isinstance(self.down_scale, tuple) or isinstance(self.down_scale, dict), "down_scale must be tuple or dict. It is {}".format(self.down_scale)
            if isinstance(self.down_scale, tuple):
                self.down_scale = dict(zip(self.agents, [self.down_scale for _ in enumerate(self.agents)]))
            if isinstance(self.down_scale, dict):
                for agent in self.agents:
                    assert agent in self.down_scale.keys(), "Agent id {} is not a key of down_scale {}".format(agent, self.down_scale)

        if self.reshape is not None:
            assert self.reshape in OBS_RESHAPE_LIST, "reshape must be in {}".format(OBS_RESHAPE_LIST)
        
        if self.range_scale is not None:
            assert isinstance(self.range_scale, tuple) or isinstance(self.range_scale, dict) or isinstance(self.range_scale, str), "range_scale must be tuple or dict. It is {}".format(self.range_scale)
            if isinstance(self.range_scale, tuple):
                self.range_scale = dict(zip(self.agents, [self.range_scale for _ in enumerate(self.agents)]))
            if isinstance(self.range_scale, dict):
                for agent in self.agents:
                    assert agent in self.range_scale.keys(), "Agent id {} is not a key of range_scale {}".format(agent, self.range_scale)
                    assert len(self.range_scale[agent]) == 2, "Length of range_scale for agent {} is not 2.".format(agent)
                    assert self.range_scale[agent][0] <= self.range_scale[agent][1], "range_scale: for agent {}, low is greater than high".format(agent)

        assert isinstance(self.frame_stacking, int) and self.frame_stacking >= 1, "frame_stacking should be int and at least 1. It is {}".format(self.frame_stacking)                    

        if self.new_dtype is not None:
            assert isinstance(self.new_dtype, type) or isinstance(self.new_dtype, dict), "new_dtype must be type or dict. It is {}".format(self.new_dtype)
            if isinstance(self.new_dtype, type):
                self.new_dtype = dict(zip(self.agents, [self.new_dtype for _ in enumerate(self.agents)]))            
            if isinstance(self.new_dtype, dict):
                for agent in self.agents:
                    assert agent in self.new_dtype.keys(), "Agent id {} is not a key of new_dtype {}".format(agent, self.new_dtype)
                    assert isinstance(self.new_dtype[agent], type), "new_dtype[agent] must be a dict of types. It is {}".format(self.new_dtype[agent])

    def _check_box_space(self):
        '''
        Checks if all observation spaces are box.

        Returns
        -------
        boolean.
        '''
        return all([isinstance(obs_space, Box) for obs_space in self.observation_spaces.values()])
        
    def modify_observation_space(self):
        # reduce color channels to 1
        if self.color_reduction is not None:
            for agent in self.agents:
                obs_space = self.observation_spaces[agent]
                dtype = obs_space.dtype
                color_reduction = self.color_reduction[agent]
                if color_reduction == 'R':
                    low = obs_space.low[:, :, 0]
                    high = obs_space.high[:, :, 0]
                if color_reduction == 'G':
                    low = obs_space.low[:, :, 1]
                    high = obs_space.high[:, :, 1]
                if color_reduction == 'B':
                    low = obs_space.low[:, :, 2]
                    high = obs_space.high[:, :, 2]
                if color_reduction == 'full':
                    # TODO: do grayscale
                    low = np.average(obs_space.low, weights=[0.299, 0.587, 0.114], axis=2).astype(obs_space.dtype)
                    high = np.average(obs_space.high, weights=[0.299, 0.587, 0.114], axis=2).astype(obs_space.dtype)
                self.observation_spaces[agent] = Box(low=low, high=high, dtype=dtype)
            print("Mod obs space: color_reduction", self.observation_spaces)
        
        # downscale (image, typically)
        if self.down_scale is not None:
            for agent in self.agents:
                obs_space = self.observation_spaces[agent]
                dtype = obs_space.dtype
                down_scale = self.down_scale[agent]
                shape = obs_space.shape
                new_shape = tuple([int(shape[i]/down_scale[i]) for i in range(len(shape))])
                low = obs_space.low.flatten()[:np.product(new_shape)].reshape(new_shape)
                high = obs_space.high.flatten()[:np.product(new_shape)].reshape(new_shape)
                self.observation_spaces[agent] = Box(low=low, high=high, dtype=dtype)
            print("Mod obs space: down_scale", self.observation_spaces)
        
        # expand dimensions by 1 or flatten the array
        if self.reshape is not None:
            for agent in self.agents:
                obs_space = self.observation_spaces[agent]
                reshape = self.reshape
                dtype = obs_space.dtype
                if reshape is OBS_RESHAPE_LIST[0]:
                    # expand dim by 1
                    low = np.expand_dims(obs_space.low, axis=-1)
                    high = np.expand_dims(obs_space.high, axis=-1)
                elif reshape is OBS_RESHAPE_LIST[1]:
                    # flatten
                    low = obs_space.low.flatten()
                    high = obs_space.high.flatten()
                self.observation_spaces[agent] = Box(low=low, high=high, dtype=dtype)
            print("Mod obs space: reshape", self.observation_spaces)
        
        # scale observation value (to [0,1], typically) and change observation_space dtype
        if self.range_scale is not None:
            for agent in self.agents:
                obs_space = self.observation_spaces[agent]
                range_scale = self.range_scale[agent]
                if self.new_dtype is not None:
                    dtype = self.new_dtype[agent]
                else:
                    dtype = obs_space.dtype
                min_obs, max_obs = range_scale
                low = np.subtract(np.divide(obs_space.low, max_obs-min_obs, dtype=dtype), min_obs)
                high = np.subtract(np.divide(obs_space.high, max_obs-min_obs, dtype=dtype), min_obs)
                self.observation_spaces[agent] = Box(low=low, high=high, dtype=dtype)
            print("Mod obs space: range_scale", self.observation_spaces)
        elif self.new_dtype is not None:
            for agent in self.agents:
                dtype = self.new_dtype[agent]
                low = obs_space.low
                high = obs_space.high
                self.observation_spaces[agent] = Box(low=low, high=high, dtype=dtype)
            print("Mod obs space: new_dtype", self.observation_spaces)
            
        if self.frame_stacking > 1:
            self.observation_spaces = stack_obs_space(self.observation_spaces, self.frame_stacking)
            print("Mod obs space: frame_stacking", self.observation_spaces)

    def modify_observations(self, observation):
        # reduce color channels to 1
        if self.color_reduction is not None:
            # TODO: any other method?? 
            # reducing the array by *adding* the last axis values
            for agent in self.agents:
                obs = observation[agent]
                color_reduction = self.color_reduction[agent]
                if color_reduction == 'R':
                    obs = obs[:, :, 0]
                if color_reduction == 'G':
                    obs = obs[:, :, 1]
                if color_reduction == 'B':
                    obs = obs[:, :, 2]
                if color_reduction == 'full':
                    # TODO: do grayscale
                    obs = np.average(obs, weights=[0.299, 0.587, 0.114], axis=2).astype(obs.dtype)
                observation[agent] = obs                
        
        # downscale (image, typically)
        if self.down_scale is not None:
            for agent in self.agents:
                obs = observation[agent]
                down_scale = self.down_scale[agent]
                mean = lambda x, axis: np.mean(x, axis=axis, dtype=np.uint8)
                obs = measure.block_reduce(obs, block_size=down_scale, func=mean)
                observation[agent] = obs
        
        # expand dimensions by 1 or flatten the array
        if self.reshape is not None:
            for agent in self.agents:
                obs = observation[agent]
                reshape = self.reshape
                dtype = obs.dtype
                if reshape is OBS_RESHAPE_LIST[0]:
                    # expand dim by 1
                    obs = np.expand_dims(obs, axis=-1)
                elif reshape is OBS_RESHAPE_LIST[1]:
                    # flatten
                    obs = obs.flatten()
                observation[agent] = obs
        
        # scale observation value (to [0,1], typically) and change observation_space dtype
        if self.range_scale is not None:
            for agent in self.agents:
                obs = observation[agent]
                range_scale = self.range_scale[agent]
                if self.new_dtype is not None:
                    dtype = self.new_dtype[agent]
                else:
                    dtype = obs.dtype
                min_obs, max_obs = range_scale
                obs = np.divide(np.subtract(obs, min_obs), max_obs-min_obs, dtype=dtype)
                observation[agent] = obs
        elif self.new_dtype is not None:
            dtype = self.new_dtype[agent]
            observation[agent] = obs.astype(dtype)

    def close(self):
        self.env.close()
    
    def render(self):
        self.env.render()
        
    def reset(self):
        obs = self.env.reset()
        self.modify_observations(obs)
        if self.frame_stacking > 1:
            self.stack_of_frames = stack_reset_obs(obs, self.frame_stacking)
            return self.stack_of_frames
        else:
            return obs
        
    def step(self, action_dict):
        obs, rewards, dones, infos = self.env.step(action_dict)

        self.modify_observations(obs)
        if self.frame_stacking > 1:
            stack_obs(self.stack_of_frames, obs)
            observations = self.stack_of_frames
        else:
            observations = obs
        
        return observations, rewards, dones, infos
