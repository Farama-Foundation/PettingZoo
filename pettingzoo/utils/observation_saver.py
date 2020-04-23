from skimage.io import imsave
import os


# Save the specified agents current observation to an image
def save_observation_for_agent(env, agent):
    save_folder = "saved_observations/{}".format(env.__module__)
    os.makedirs(save_folder, exist_ok=True)

    observation = env.observe(agent)
    fname = os.path.join(save_folder, str(agent) + ".png")
    imsave(fname, observation)


# Save the env.agent_selection agent observation to an image
def save_observation_selected(env):
    agent = env.agent_selection
    save_observation_for_agent(env, agent)


# Save observations of all agents in env to images
def save_observation_for_all(env):
    save_folder = "saved_observations/{}".format(env.__module__)
    os.makedirs(save_folder, exist_ok=True)

    for agent in env.agent_order:
        observation = env.observe(agent)
        fname = os.path.join(save_folder, str(agent) + ".png")
        imsave(fname, observation)
