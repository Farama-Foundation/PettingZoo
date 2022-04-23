import sys
from copy import deepcopy

import numpy as np
import pytest
from gym import spaces
from supersuit import (agent_indicator_v0, black_death_v3, clip_actions_v0,
                       clip_reward_v0, color_reduction_v0,
                       delay_observations_v0, dtype_v0, flatten_v0,
                       frame_skip_v0, frame_stack_v1, max_observation_v0,
                       nan_random_v0, nan_zeros_v0, normalize_obs_v0,
                       pad_action_space_v0, pad_observations_v0,
                       scale_actions_v0, sticky_actions_v0)

from .all_modules import all_environments


def observation_homogenizable(env):
    homogenizable = True
    for key in env.observation_spaces:
        homogenizable = homogenizable and (
            isinstance(env.observation_spaces[key], spaces.Box)
            or isinstance(env.observation_spaces[key], spaces.Discrete)
        )
    return homogenizable


def action_homogenizable(env):
    homogenizable = True
    for key in env.action_spaces:
        homogenizable = homogenizable and (
            isinstance(env.action_spaces[key], spaces.Box)
            or isinstance(env.action_spaces[key], spaces.Discrete)
        )
    return homogenizable


def image_observation(env):
    imagable = True
    for key in env.observation_spaces:
        if isinstance(env.observation_spaces[key], spaces.Box):
            imagable = imagable and (env.observation_spaces[key].low.shape == 3)
            imagable = imagable and (len(env.observation_spaces[key].shape[2]) == 3)
            imagable = imagable and (env.observation_spaces[key].low == 0).all()
            imagable = imagable and (env.observation_spaces[key].high == 255).all()
        else:
            return False
    return imagable


def box_action(env):
    boxable = True
    for key in env.action_spaces:
        boxable = boxable and isinstance(env.action_spaces[key], spaces.Box)
    return boxable


def not_dict_observation(env):
    is_dict = True
    for key in env.observation_spaces:
        is_dict = is_dict and (isinstance(env.observation_spaces[key], spaces.Dict))
    return not is_dict


def not_discrete_observation(env):
    is_discrete = True
    for key in env.observation_spaces:
        is_discrete = is_discrete and (
            isinstance(env.observation_spaces[key], spaces.Discrete)
        )
    return not is_discrete


@pytest.mark.parametrize(("name", "env_module"), list(all_environments.items()))
def test_unwrapped(name, env_module):

    env = env_module.env()
    base_env = env.unwrapped

    if image_observation(env):
        env = max_observation_v0(env, 2)
        env = color_reduction_v0(env, mode="full")
        env = normalize_obs_v0(env)

    if box_action(env):
        env = clip_actions_v0(env)
        env = scale_actions_v0(env, 0.5)

    if observation_homogenizable(env):
        env = pad_observations_v0(env)
        env = frame_stack_v1(env, 2)
        env = agent_indicator_v0(env)
        env = black_death_v3(env)

    if not_dict_observation(env) and not_discrete_observation(env):
        env = dtype_v0(env, np.float16)
        env = flatten_v0(env)
        env = frame_skip_v0(env, 2)

    if action_homogenizable(env):
        env = pad_action_space_v0(env)

    env = clip_reward_v0(env, lower_bound=-1, upper_bound=1)
    env = delay_observations_v0(env, 2)
    env = sticky_actions_v0(env, 0.5)
    env = nan_random_v0(env)
    env = nan_zeros_v0(env)

    assert env.unwrapped == base_env, "Unwrapped Test: unequal envs"
