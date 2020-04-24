from skimage.io import imsave
import numpy as np
import gym
import os


def _check_observation_saveable(env, agent):
    assert isinstance(env.observation_spaces[agent], gym.spaces.Box), "Observations must be Box to save observations as image"
    assert np.all(np.equal(env.observation_spaces[agent].low, 0)) and np.all(np.equal(env.observation_spaces[agent].high, 255)), "Observations must be 0 to 255 to save as image"
    assert len(env.observation_spaces[agent].shape) == 3 or len(env.observation_spaces[agent].shape) == 2, "Observations must be 2D or 3D to save as image"
    if len(env.observation_spaces[agent].shape) == 3:
        assert env.observation_spaces[agent].shape[2] == 1 or env.observation_spaces[agent].shape[2] == 3, "3D observations can only have 1 or 3 channels to save as an image"


# Save the specified agents current observation to an image
def save_observation_for_agent(env, agent, save_dir=os.getcwd()):
    _check_observation_saveable(env, agent)
    save_folder = "{}/{}".format(save_dir, env.__module__)
    os.makedirs(save_folder, exist_ok=True)

    observation = env.observe(agent)
    fname = os.path.join(save_folder, str(agent) + ".png")
    imsave(fname, observation)


# Save the env.agent_selection agent observation to an image
def save_observation_selected(env, save_dir=os.getcwd()):
    agent = env.agent_selection
    save_observation_for_agent(env, agent)


# Save observations of all agents in env to images
def save_observation_for_all(env, save_dir=os.getcwd()):
    save_folder = "{}/{}".format(save_dir, env.__module__)
    os.makedirs(save_folder, exist_ok=True)

    for agent in env.agent_order:
        _check_observation_saveable(env, agent)
        observation = env.observe(agent)
        fname = os.path.join(save_folder, str(agent) + ".png")
        imsave(fname, observation)
