import os

import imageio
import numpy as np
import torch
from agilerl.algorithms.dqn import DQN
from agilerl.utils.utils import observation_space_channels_to_first
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
    observation_spaces = [
        env.observation_space(agent)["observation"] for agent in env.agents
    ]
    action_spaces = [env.action_space(agent) for agent in env.agents]

    # Instantiate an DQN object
    dqn = DQN(
        observation_space=observation_space_channels_to_first(observation_spaces[0]),
        action_space=action_spaces[0],
        device=device,
    )

    # Load the saved algorithm into the DQN object
    dqn.load_checkpoint(path)

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
                            action = opponent.get_action(
                                state, epsilon=0, action_mask=action_mask
                            )[0]
                        elif opponent_difficulty == "random":
                            action = opponent.get_action(action_mask)
                        else:
                            action = opponent.get_action(player=0)
                    else:
                        action = dqn.get_action(
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
                            action = opponent.get_action(
                                state, epsilon=0, action_mask=action_mask
                            )[0]
                        elif opponent_difficulty == "random":
                            action = opponent.get_action(action_mask)
                        else:
                            action = opponent.get_action(player=1)
                    else:
                        action = dqn.get_action(
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
