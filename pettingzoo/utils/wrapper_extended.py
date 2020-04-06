from pettingzoo.utils import wrapper

COLOR_RED_LIST = ["full", 'R', 'G', 'B']
OBS_RESHAPE_LIST = ["expand", "flatten"]


class wrapper_extended(wrapper):

    def __init__(self, env, _pre_color_reduction_obs_space=None, _pre_color_reduction_obs=None, color_reduction=None, _pre_down_scale_obs_space=None, _pre_down_scale_obs=None, down_scale=None, _pre_reshape_obs_space=None, _pre_reshape_obs=None, reshape=None, _pre_range_scale_obs_space=None, _pre_range_scale_obs=None, range_scale=None, new_dtype=None, continuous_actions=False, _pre_frame_stacking_obs_space=None, _pre_frame_stacking_obs=None, frame_stacking=1, _final_processing_obs_space=None, _final_processing_obs=None):

        self._pre_color_reduction_obs_space = _pre_color_reduction_obs_space
        self._pre_down_scale_obs_space = _pre_down_scale_obs_space
        self._pre_reshape_obs_space = _pre_reshape_obs_space
        self._pre_range_scale_obs_space = _pre_range_scale_obs_space
        self._pre_frame_stacking_obs_space = _pre_frame_stacking_obs_space
        self._final_processing_obs_space = _final_processing_obs_space

        self._pre_color_reduction_obs = _pre_color_reduction_obs
        self._pre_down_scale_obs = _pre_down_scale_obs
        self._pre_reshape_obs = _pre_reshape_obs
        self._pre_range_scale_obs = _pre_range_scale_obs
        self._pre_frame_stacking_obs = _pre_frame_stacking_obs
        self._final_processing_obs = _final_processing_obs

        super().__init__(env=env, color_reduction=color_reduction, down_scale=down_scale, reshape=reshape, range_scale=range_scale, new_dtype=new_dtype, continuous_actions=continuous_actions, frame_stacking=frame_stacking)

    def modify_observation_space(self):
        if self._pre_color_reduction_obs_space is not None:
            self._pre_color_reduction_obs_space(self.env, self.observation_spaces, self.action_spaces)

        # reduce color channels to 1
        if self.color_reduction is not None:
            self._color_reduction_obs_space()

        if self._pre_down_scale_obs_space is not None:
            self._pre_down_scale_obs_space(self.env, self.observation_spaces, self.action_spaces)

        # downscale (image, typically)
        if self.down_scale is not None:
            self._down_scale_obs_space()

        if self._pre_reshape_obs_space is not None:
            self._pre_reshape_obs_space(self.env, self.observation_spaces, self.action_spaces)

        # expand dimensions by 1 or flatten the array
        if self.reshape is not None:
            self._reshape_obs_space()

        if self._pre_range_scale_obs_space is not None:
            self._pre_range_scale_obs_space(self.env, self.observation_spaces, self.action_spaces)

        # scale observation value (to [0,1], typically) and change observation_space dtype
        if self.range_scale is not None:
            self._range_scale_obs_space()
        elif self.new_dtype is not None:
            self._new_dtype_obs_space()

        if self._pre_frame_stacking_obs_space is not None:
            self._pre_frame_stacking_obs_space(self.env, self.observation_spaces, self.action_spaces)

        if self.frame_stacking > 1:
            self._frame_stacking_obs_space()

        if self._final_processing_obs_space is not None:
            self._final_processing_obs_space(self.env, self.observation_spaces, self.action_spaces)

    def modify_observation(self, agent, observation):
        obs = observation
        if self._pre_color_reduction_obs is not None:
            obs = self._pre_color_reduction_obs(obs, agent)

        # reduce color channels to 1
        if self.color_reduction is not None:
            obs = self._color_reduction_obs(obs, agent)

        if self._pre_down_scale_obs is not None:
            obs = self._pre_down_scale_obs(obs, agent)

        # downscale (image, typically)
        if self.down_scale is not None:
            obs = self._down_scale_obs(obs, agent)

        if self._pre_reshape_obs is not None:
            obs = self._pre_reshape_obs(obs, agent)

        # expand dimensions by 1 or flatten the array
        if self.reshape is not None:
            obs = self._reshape_obs(obs, agent)

        if self._pre_range_scale_obs is not None:
            obs = self._pre_range_scale_obs(obs, agent)

        # scale observation value (to [0,1], typically) and change observation_space dtype
        if self.range_scale is not None:
            obs = self._range_scale_obs(obs, agent)
        elif self.new_dtype is not None:
            obs = self._new_dtype_obs(obs, agent)

        if self._pre_frame_stacking_obs is not None:
            obs = self._pre_frame_stacking_obs(obs, agent)

        # frame_stacking
        if self.frame_stacking > 1:
            obs = self._frame_stacking_obs(obs, agent)

        if self._final_processing_obs is not None:
            obs = self._final_processing_obs(obs, agent)

        return obs
