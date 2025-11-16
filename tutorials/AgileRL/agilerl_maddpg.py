"""This tutorial shows how to train an MADDPG agent on the space invaders atari environment.

Authors: Michael (https://github.com/mikepratt1), Nick (https://github.com/nicku-a), Jaime (https://github.com/jaimesabalbermudez)
"""

import os
from copy import deepcopy

import numpy as np
import supersuit as ss
import torch
from agilerl.algorithms.core.registry import HyperparameterConfig, RLParameter
from agilerl.components.multi_agent_replay_buffer import MultiAgentReplayBuffer
from agilerl.utils.algo_utils import obs_channels_to_first
from agilerl.utils.utils import create_population, observation_space_channels_to_first
from agilerl.vector.pz_async_vec_env import AsyncPettingZooVecEnv
from tqdm import trange

from pettingzoo.atari import space_invaders_v2

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Define the network configuration
    NET_CONFIG = {
        "encoder_config": {
            "channel_size": [32, 32],  # CNN channel size
            "kernel_size": [1, 1],  # CNN kernel size
            "stride_size": [2, 2],  # CNN stride size
        },
        "head_config": {"hidden_size": [32, 32]},  # Actor head hidden size
    }

    # Define the initial hyperparameters
    INIT_HP = {
        "POPULATION_SIZE": 1,
        "ALGO": "MADDPG",  # Algorithm
        # Swap image channels dimension from last to first [H, W, C] -> [C, H, W]
        "CHANNELS_LAST": True,
        "BATCH_SIZE": 32,  # Batch size
        "O_U_NOISE": True,  # Ornstein Uhlenbeck action noise
        "EXPL_NOISE": 0.1,  # Action noise scale
        "MEAN_NOISE": 0.0,  # Mean action noise
        "THETA": 0.15,  # Rate of mean reversion in OU noise
        "DT": 0.01,  # Timestep for OU noise
        "LR_ACTOR": 0.001,  # Actor learning rate
        "LR_CRITIC": 0.001,  # Critic learning rate
        "GAMMA": 0.95,  # Discount factor
        "MEMORY_SIZE": 100000,  # Max memory buffer size
        "LEARN_STEP": 100,  # Learning frequency
        "TAU": 0.01,  # For soft update of target parameters
    }

    num_envs = 8
    # Define the space invaders environment as a parallel environment
    env = space_invaders_v2.parallel_env()

    # Environment processing for image based observations
    env = ss.frame_skip_v0(env, 4)
    env = ss.clip_reward_v0(env, lower_bound=-1, upper_bound=1)
    env = ss.color_reduction_v0(env, mode="B")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.frame_stack_v1(env, 4)
    env = AsyncPettingZooVecEnv([lambda: env for _ in range(num_envs)])

    env.reset()

    # Configure the multi-agent algo input arguments
    observation_spaces = [env.single_observation_space(agent) for agent in env.agents]
    action_spaces = [env.single_action_space(agent) for agent in env.agents]
    if INIT_HP["CHANNELS_LAST"]:
        observation_spaces = [
            observation_space_channels_to_first(obs) for obs in observation_spaces
        ]

    # Append number of agents and agent IDs to the initial hyperparameter dictionary
    INIT_HP["AGENT_IDS"] = env.agents

    # Mutation config for RL hyperparameters
    hp_config = HyperparameterConfig(
        lr_actor=RLParameter(min=1e-4, max=1e-2),
        lr_critic=RLParameter(min=1e-4, max=1e-2),
        batch_size=RLParameter(min=8, max=512, dtype=int),
        learn_step=RLParameter(
            min=20, max=200, dtype=int, grow_factor=1.5, shrink_factor=0.75
        ),
    )

    # Create a population ready for evolutionary hyper-parameter optimisation
    agent = create_population(
        INIT_HP["ALGO"],
        observation_spaces,
        action_spaces,
        NET_CONFIG,
        INIT_HP,
        hp_config,
        population_size=INIT_HP["POPULATION_SIZE"],
        num_envs=num_envs,
        device=device,
    )[0]

    # Configure the multi-agent replay buffer
    field_names = ["state", "action", "reward", "next_state", "done"]
    memory = MultiAgentReplayBuffer(
        INIT_HP["MEMORY_SIZE"],
        field_names=field_names,
        agent_ids=INIT_HP["AGENT_IDS"],
        device=device,
    )

    # Define training loop parameters
    agent_ids = deepcopy(env.agents)
    max_steps = 20000  # Max steps (default: 2000000)
    learning_delay = 500  # Steps before starting learning
    training_steps = 10000  # Frequency at which we evaluate training score
    eval_steps = None  # Evaluation steps per episode - go until done
    eval_loop = 1  # Number of evaluation episodes

    total_steps = 0

    # TRAINING LOOP
    print("Training...")
    pbar = trange(max_steps, unit="step")
    while np.less(agent.steps[-1], max_steps):
        state, info = env.reset()  # Reset environment at start of episode
        scores = np.zeros((num_envs, len(agent_ids)))
        completed_episode_scores = []
        steps = 0
        if INIT_HP["CHANNELS_LAST"]:
            state = {
                agent_id: obs_channels_to_first(s) for agent_id, s in state.items()
            }

        for idx_step in range(training_steps // num_envs):
            # Get next action from agent
            cont_actions, discrete_action = agent.get_action(
                obs=state, training=True, infos=info
            )
            if agent.discrete_actions:
                action = discrete_action
            else:
                action = cont_actions

            # Act in environment
            action = {agent: env.action_space(agent).sample() for agent in env.agents}
            next_state, reward, termination, truncation, info = env.step(action)
            if not termination:
                assert False
            scores += np.array(list(reward.values())).transpose()
            total_steps += num_envs
            steps += num_envs

            # Image processing if necessary for the environment
            if INIT_HP["CHANNELS_LAST"]:
                next_state = {
                    agent_id: obs_channels_to_first(ns)
                    for agent_id, ns in next_state.items()
                }

            # Save experiences to replay buffer
            memory.save_to_memory(
                state,
                cont_actions,
                reward,
                next_state,
                termination,
                is_vectorised=True,
            )

            # Learn according to learning frequency
            # Handle learn steps > num_envs
            if agent.learn_step > num_envs:
                learn_step = agent.learn_step // num_envs
                if (
                    idx_step % learn_step == 0
                    and len(memory) >= agent.batch_size
                    and memory.counter > learning_delay
                ):
                    # Sample replay buffer
                    experiences = memory.sample(agent.batch_size)
                    # Learn according to agent's RL algorithm
                    agent.learn(experiences)
            # Handle num_envs > learn step; learn multiple times per step in env
            elif len(memory) >= agent.batch_size and memory.counter > learning_delay:
                for _ in range(num_envs // agent.learn_step):
                    # Sample replay buffer
                    experiences = memory.sample(agent.batch_size)
                    # Learn according to agent's RL algorithm
                    agent.learn(experiences)

            state = next_state

            # Calculate scores and reset noise for finished episodes
            reset_noise_indices = []
            term_array = np.array(list(termination.values())).transpose()
            trunc_array = np.array(list(truncation.values())).transpose()
            for idx, (d, t) in enumerate(zip(term_array, trunc_array)):
                if np.any(d) or np.any(t):
                    completed_episode_scores.append(scores[idx])
                    agent.scores.append(scores[idx])
                    scores[idx] = 0
                    reset_noise_indices.append(idx)
            agent.reset_action_noise(reset_noise_indices)

        pbar.update(training_steps)

        agent.steps[-1] += steps

        # Evaluate population
        fitness = agent.test(
            env,
            swap_channels=INIT_HP["CHANNELS_LAST"],
            max_steps=eval_steps,
            loop=eval_loop,
            sum_scores=False,
        )
        pop_episode_scores = np.array(completed_episode_scores)
        mean_scores = np.mean(pop_episode_scores, axis=0)

        print(f"--- Global steps {total_steps} ---")
        print(f"Steps {agent.steps[-1]}")
        print("Scores:")
        for idx, sub_agent in enumerate(agent_ids):
            print(f"    {sub_agent} score: {mean_scores[idx]}")
        print("Fitness")
        for idx, sub_agent in enumerate(agent_ids):
            print(f"    {sub_agent} fitness: {fitness[idx]}")
        print("Previous 5 fitness avgs")
        for idx, sub_agent in enumerate(agent_ids):
            print(
                f"  {sub_agent} fitness average: {np.mean(agent.fitness[-5:], axis=0)[idx]}"
            )

        # Update step counter
        agent.steps.append(agent.steps[-1])

    # Save the trained algorithm
    path = "./models/MADDPG"
    filename = "MADDPG_trained_agent.pt"
    os.makedirs(path, exist_ok=True)
    save_path = os.path.join(path, filename)
    agent.save_checkpoint(save_path)

    pbar.close()
    env.close()
