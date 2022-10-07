import os

import gymnasium.spaces
import numpy as np


def _check_observation_saveable(env, agent):
    obs_space = env.observation_space(agent)
    assert isinstance(
        obs_space, gymnasium.spaces.Box
    ), "Observations must be Box to save observations as image"
    assert np.all(np.equal(obs_space.low, 0)) and np.all(
        np.equal(obs_space.high, 255)
    ), "Observations must be 0 to 255 to save as image"
    assert (
        len(obs_space.shape) == 3 or len(obs_space.shape) == 2
    ), "Observations must be 2D or 3D to save as image"
    if len(obs_space.shape) == 3:
        assert (
            obs_space.shape[2] == 1 or obs_space.shape[2] == 3
        ), "3D observations can only have 1 or 3 channels to save as an image"


# save the observation of an agent. If agent not specified uses env selected agent. If all_agents
# then all agents in environment observation recorded.
def save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd()):
    from PIL import Image

    if agent is None:
        agent = env.agent_selection
    agent_list = [agent]
    if all_agents:
        agent_list = env.agents[:]
    for a in agent_list:
        _check_observation_saveable(env, a)
        save_folder = "{}/{}".format(
            save_dir, str(env).replace("<", "_").replace(">", "_")
        )
        os.makedirs(save_folder, exist_ok=True)

        observation = env.observe(a)
        rescaled = observation.astype(np.uint8)
        im = Image.fromarray(rescaled)
        fname = os.path.join(save_folder, str(a) + ".png")
        im.save(fname)
