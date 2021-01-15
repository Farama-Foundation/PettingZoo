from pettingzoo.utils import save_observation
import gym
import numpy as np


def check_save_obs(env):
    for agent in env.agents:
        assert isinstance(env.observation_spaces[agent], gym.spaces.Box), "Observations must be Box to save observations as image"
        assert np.all(np.equal(env.observation_spaces[agent].low, 0)) and np.all(np.equal(env.observation_spaces[agent].high, 255)), "Observations must be 0 to 255 to save as image"
        assert len(env.observation_spaces[agent].shape) == 3 or len(env.observation_spaces[agent].shape) == 2, "Observations must be 2D or 3D to save as image"
        if len(env.observation_spaces[agent].shape) == 3:
            assert env.observation_spaces[agent].shape[2] == 1 or env.observation_spaces[agent].shape[2] == 3, "3D observations can only have 1 or 3 channels to save as an image"


def test_save_obs(env):
    env.reset()
    try:
        check_save_obs(env)
        for agent in env.agents:
            save_observation(env=env, agent=agent, save_dir="saved_observations")

    except AssertionError as ae:
        print("did not save the observations: ", ae)
