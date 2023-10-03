import os

import imageio
import numpy as np
import torch
from agilerl.algorithms.dqn import DQN
from PIL import Image, ImageDraw, ImageFont

from pettingzoo.classic import connect_four_v3


# Define function to return image
def _label_with_episode_number(frame, episode_num, frame_no):
    im = Image.fromarray(frame)
    drawer = ImageDraw.Draw(im)
    text_color = (255, 255, 255)
    font = ImageFont.truetype("arial.ttf", size=45)
    drawer.text(
        (100, 5),
        f"Episode: {episode_num+1}     Frame: {frame_no}",
        fill=text_color,
        font=font,
    )
    return im


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Configure the environment
    env = connect_four_v3.env(render_mode="rgb_array")
    env.reset()

    # Configure the algo input arguments
    state_dim = [
        env.observation_space(agent)["observation"].shape for agent in env.agents
    ]
    one_hot = False
    action_dim = [env.action_space(agent).n for agent in env.agents]

    # Pre-process dimensions for pytorch layers
    # We will use self-play, so we only need to worry about the state dim of a single agent
    # We flatten the 6x7x2 observation as input to the agent's neural network
    state_dim = np.zeros(state_dim[0]).flatten().shape
    action_dim = action_dim[0]

    # Instantiate an DQN object
    dqn = DQN(
        state_dim,
        action_dim,
        one_hot,
        device=device,
    )

    # Load the saved algorithm into the DQN object
    path = "./models/DQN/DQN_trained_agent.pt"
    dqn.loadCheckpoint(path)

    # Define test loop parameters
    episodes = 1  # Number of episodes to test agent on
    max_steps = 500  # Max number of steps to take in the environment in each episode

    rewards = []  # List to collect total episodic reward
    frames = []  # List to collect frames

    # Test loop for inference
    for ep in range(episodes):
        env.reset()  # Reset environment at start of episode
        frame = env.render()
        frames.append(_label_with_episode_number(frame, episode_num=ep, frame_no=0))
        observation, reward, done, truncation, _ = env.last()
        player = -1  # Tracker for which player's turn it is
        p1_score, p2_score = 0, 0  # Scores of player 1 and 2
        for idx_step in range(max_steps):
            if player > 0:  # Flip the pieces so the agent always behaves as player 1
                state = observation["observation"]
                state[:, :, [0, 1]] = state[:, :, [1, 0]]
                state = state.flatten()
            else:
                state = observation["observation"].flatten()
            action_mask = observation["action_mask"]

            action = dqn.getAction(state, epsilon=0, action_mask=action_mask)[
                0
            ]  # Get next action from agent
            env.step(action)  # Act in environment
            observation, reward, termination, truncation, _ = env.last()
            # Save the frame for this step and append to frames list
            frame = env.render()
            frames.append(
                _label_with_episode_number(frame, episode_num=ep, frame_no=idx_step + 1)
            )

            # Save agent's reward for this step in this episode
            if (
                player > 0
            ):  # Again, flip the pieces so the agent has the perspective of player 1
                p2_score += reward
            else:
                p1_score += reward

            # Stop episode if any agents have terminated
            if truncation or termination:
                break

            player *= -1

        print("-" * 15, f"Episode: {ep+1}", "-" * 15)
        print(f"Episode length: {idx_step}")
        print(f"Player score: {p1_score}")
        print(f"Player score: {p2_score}")

    env.close()

    # Save the gif to specified path
    gif_path = "./videos/"
    os.makedirs(gif_path, exist_ok=True)
    imageio.mimwrite(
        os.path.join("./videos/", "connect_four_self_play.gif"), frames, duration=300
    )
