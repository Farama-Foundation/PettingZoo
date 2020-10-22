from cv2 import imwrite
import numpy as np
import gym
import os


def _check_observation_saveable(env, agent):
    assert isinstance(env.observation_spaces[agent], gym.spaces.Box), "Observations must be Box to save observations as image"
    assert np.all(np.equal(env.observation_spaces[agent].low, 0)) and np.all(np.equal(env.observation_spaces[agent].high, 255)), "Observations must be 0 to 255 to save as image"
    assert len(env.observation_spaces[agent].shape) == 3 or len(env.observation_spaces[agent].shape) == 2, "Observations must be 2D or 3D to save as image"
    if len(env.observation_spaces[agent].shape) == 3:
        assert env.observation_spaces[agent].shape[2] == 1 or env.observation_spaces[agent].shape[2] == 3, "3D observations can only have 1 or 3 channels to save as an image"


# save the observation of an agent. If agent not specified uses env selected agent. If all_agents
# then all agents in environment observation recorded.
def save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd()):
    if agent is None:
        agent = env.agent_selection
    agent_list = [agent]
    if all_agents:
        agent_list = env.agents[:]
    for a in agent_list:
        _check_observation_saveable(env, a)
        save_folder = "{}/{}".format(save_dir, env.__module__)
        os.makedirs(save_folder, exist_ok=True)

        observation = env.observe(a)
        fname = os.path.join(save_folder, str(a) + ".png")
        imwrite(fname, observation)
