import os

import imageio
import numpy as np
import torch
from agilerl.algorithms.dqn import DQN
from agilerl_dqn_curriculum import Opponent
from PIL import Image, ImageDraw, ImageFont

from pettingzoo.classic import connect_four_v3


# Define function to return image
def _label_with_episode_number(frame, episode_num, frame_no, p):
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
    if p == 1:
        player = "Player 1"
        color = (255, 0, 0)
    if p == 2:
        player = "Player 2"
        color = (100, 255, 150)
    if p is None:
        player = "Self-play"
        color = (255, 255, 255)
    drawer.text((700, 5), f"Agent: {player}", fill=color, font=font)
    return im


# Resizes frames to make file size smaller
def resize_frames(frames, fraction):
    resized_frames = []
    for img in frames:
        new_width = int(img.width * fraction)
        new_height = int(img.height * fraction)
        img_resized = img.resize((new_width, new_height))
        resized_frames.append(np.array(img_resized))

    return resized_frames


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    path = "./models/DQN/lesson3_trained_agent.pt"  # Path to saved agent checkpoint

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
    dqn.loadCheckpoint(path)

    for opponent_difficulty in ["random", "weak", "strong", "self"]:
        # Create opponent
        if opponent_difficulty == "self":
            opponent = dqn
        else:
            opponent = Opponent(env, opponent_difficulty)

        # Define test loop parameters
        episodes = 2  # Number of episodes to test agent on
        max_steps = (
            500  # Max number of steps to take in the environment in each episode
        )

        rewards = []  # List to collect total episodic reward
        frames = []  # List to collect frames

        print("============================================")
        print(f"Agent: {path}")
        print(f"Opponent: {opponent_difficulty}")

        # Test loop for inference
        for ep in range(episodes):
            if ep / episodes < 0.5:
                opponent_first = False
                p = 1
            else:
                opponent_first = True
                p = 2
            if opponent_difficulty == "self":
                p = None
            env.reset()  # Reset environment at start of episode
            frame = env.render()
            frames.append(
                _label_with_episode_number(frame, episode_num=ep, frame_no=0, p=p)
            )
            observation, reward, done, truncation, _ = env.last()
            player = -1  # Tracker for which player's turn it is
            score = 0
            for idx_step in range(max_steps):
                action_mask = observation["action_mask"]
                if player < 0:
                    state = np.moveaxis(observation["observation"], [-1], [-3])
                    state = np.expand_dims(state, 0)
                    if opponent_first:
                        if opponent_difficulty == "self":
                            action = opponent.getAction(
                                state, epsilon=0, action_mask=action_mask
                            )[0]
                        elif opponent_difficulty == "random":
                            action = opponent.getAction(action_mask)
                        else:
                            action = opponent.getAction(player=0)
                    else:
                        action = dqn.getAction(
                            state, epsilon=0, action_mask=action_mask
                        )[
                            0
                        ]  # Get next action from agent
                if player > 0:
                    state = np.moveaxis(observation["observation"], [-1], [-3])
                    state[[0, 1], :, :] = state[[0, 1], :, :]
                    state = np.expand_dims(state, 0)
                    if not opponent_first:
                        if opponent_difficulty == "self":
                            action = opponent.getAction(
                                state, epsilon=0, action_mask=action_mask
                            )[0]
                        elif opponent_difficulty == "random":
                            action = opponent.getAction(action_mask)
                        else:
                            action = opponent.getAction(player=1)
                    else:
                        action = dqn.getAction(
                            state, epsilon=0, action_mask=action_mask
                        )[
                            0
                        ]  # Get next action from agent
                env.step(action)  # Act in environment
                observation, reward, termination, truncation, _ = env.last()
                # Save the frame for this step and append to frames list
                frame = env.render()
                frames.append(
                    _label_with_episode_number(
                        frame, episode_num=ep, frame_no=idx_step, p=p
                    )
                )

                if (player > 0 and opponent_first) or (
                    player < 0 and not opponent_first
                ):
                    score += reward
                else:
                    score -= reward

                # Stop episode if any agents have terminated
                if truncation or termination:
                    break

                player *= -1

            print("-" * 15, f"Episode: {ep+1}", "-" * 15)
            print(f"Episode length: {idx_step}")
            print(f"Score: {score}")

        print("============================================")

        frames = resize_frames(frames, 0.5)

        # Save the gif to specified path
        gif_path = "./videos/"
        os.makedirs(gif_path, exist_ok=True)
        imageio.mimwrite(
            os.path.join("./videos/", f"connect_four_{opponent_difficulty}_opp.gif"),
            frames,
            duration=400,
            loop=True,
        )

    env.close()
