import os

import imageio
import numpy as np
import supersuit as ss
import torch
from agilerl.algorithms.maddpg import MADDPG
from agilerl.utils.algo_utils import obs_channels_to_first
from agilerl.utils.utils import observation_space_channels_to_first
from PIL import Image, ImageDraw

from pettingzoo.atari import space_invaders_v2


# Define function to return image
def _label_with_episode_number(frame, episode_num):
    im = Image.fromarray(frame)

    drawer = ImageDraw.Draw(im)

    if np.mean(frame) < 128:
        text_color = (255, 255, 255)
    else:
        text_color = (0, 0, 0)
    drawer.text(
        (im.size[0] / 20, im.size[1] / 18), f"Episode: {episode_num+1}", fill=text_color
    )

    return im


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Configure the environment
    env = space_invaders_v2.parallel_env(render_mode="rgb_array")
    channels_last = True  # Needed for environments that use images as observations
    if channels_last:
        # Environment processing for image based observations
        env = ss.frame_skip_v0(env, 4)
        env = ss.clip_reward_v0(env, lower_bound=-1, upper_bound=1)
        env = ss.color_reduction_v0(env, mode="B")
        env = ss.resize_v1(env, x_size=84, y_size=84)
        env = ss.frame_stack_v1(env, 4)

    env.reset()

    observation_spaces = [env.observation_space(agent) for agent in env.agents]
    action_spaces = [env.action_space(agent) for agent in env.agents]

    # Pre-process image dimensions for pytorch convolutional layers
    if channels_last:
        observation_spaces = [
            observation_space_channels_to_first(space) for space in observation_spaces
        ]

    # Append number of agents and agent IDs to the initial hyperparameter dictionary
    n_agents = env.num_agents
    agent_ids = env.agents

    # Instantiate an MADDPG object
    maddpg = MADDPG(
        observation_spaces=observation_spaces,
        action_spaces=action_spaces,
        agent_ids=agent_ids,
        device=device,
    )

    # Load the saved algorithm into the MADDPG object
    path = "./models/MADDPG/MADDPG_trained_agent.pt"
    maddpg.load_checkpoint(path)

    # Define test loop parameters
    episodes = 10  # Number of episodes to test agent on
    max_steps = 500  # Max number of steps to take in the environment in each episode

    rewards = []  # List to collect total episodic reward
    frames = []  # List to collect frames
    indi_agent_rewards = {
        agent_id: [] for agent_id in agent_ids
    }  # Dictionary to collect inidivdual agent rewards

    # Test loop for inference
    for ep in range(episodes):
        state, info = env.reset()
        agent_reward = {agent_id: 0 for agent_id in agent_ids}
        score = 0
        for _ in range(max_steps):
            if channels_last:
                state = {
                    agent_id: obs_channels_to_first(s) for agent_id, s in state.items()
                }

            agent_mask = info["agent_mask"] if "agent_mask" in info.keys() else None
            env_defined_actions = (
                info["env_defined_actions"]
                if "env_defined_actions" in info.keys()
                else None
            )

            # Get next action from agent
            cont_actions, discrete_action = maddpg.get_action(state, training=False)

            if maddpg.discrete_actions:
                action = discrete_action
            else:
                action = cont_actions

            # Save the frame for this step and append to frames list
            frame = env.render()
            frames.append(_label_with_episode_number(frame, episode_num=ep))

            # Take action in environment
            action = {agent_id: a[0] for agent_id, a in action.items()}
            state, reward, termination, truncation, info = env.step(action)

            # Save agent's reward for this step in this episode
            for agent_id, r in reward.items():
                agent_reward[agent_id] += r

            # Determine total score for the episode and then append to rewards list
            score = sum(agent_reward.values())

            # Stop episode if any agents have terminated
            if any(truncation.values()) or any(termination.values()):
                break

        rewards.append(score)

        # Record agent specific episodic reward for each agent
        for agent_id in agent_ids:
            indi_agent_rewards[agent_id].append(agent_reward[agent_id])

        print("-" * 15, f"Episode: {ep}", "-" * 15)
        print("Episodic Reward: ", rewards[-1])
        for agent_id, reward_list in indi_agent_rewards.items():
            print(f"{agent_id} reward: {reward_list[-1]}")

    env.close()

    # Save the gif to specified path
    gif_path = "./videos/"
    os.makedirs(gif_path, exist_ok=True)
    imageio.mimwrite(
        os.path.join("./videos/", "space_invaders.gif"), frames, duration=10
    )
