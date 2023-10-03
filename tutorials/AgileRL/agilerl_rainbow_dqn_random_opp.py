"""This tutorial shows how to train a Rainbow DQN agent on the connect four environment.

Authors: Nick (https://github.com/nicku-a)
"""
import os
import random
from datetime import datetime

import numpy as np
import torch
import wandb
from agilerl.components.replay_buffer import (
    MultiStepReplayBuffer,
    PrioritizedReplayBuffer,
    ReplayBuffer,
)
from agilerl.hpo.mutation import Mutations
from agilerl.hpo.tournament import TournamentSelection
from agilerl.utils.utils import initialPopulation
from tqdm import trange

from pettingzoo.classic import connect_four_v3

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("===== AgileRL vs Random Opponent Agent Demo - Rainbow DQN =====")

    # Define the network configuration
    NET_CONFIG = {
        "arch": "mlp",  # Network architecture
        "h_size": [64, 128, 128],  # Actor hidden size
    }

    # Define the initial hyperparameters
    INIT_HP = {
        "POPULATION_SIZE": 1,
        "ALGO": "Rainbow DQN",  # Algorithm
        # Swap image channels dimension from last to first [H, W, C] -> [C, H, W]
        "BATCH_SIZE": 256,  # Batch size
        "LR": 1e-3,  # Learning rate
        "GAMMA": 0.99,  # Discount factor
        "MEMORY_SIZE": 10000,  # Max memory buffer size
        "LEARN_STEP": 1,  # Learning frequency
        "N_STEP": 3,  # Step number to calculate td error
        "PER": True,  # Use prioritized experience replay buffer
        "ALPHA": 0.6,  # Prioritized replay buffer parameter
        "TAU": 0.01,  # For soft update of target parameters
        "BETA": 0.4,  # Importance sampling coefficient
        "PRIOR_EPS": 0.000001,  # Minimum priority for sampling
        "NUM_ATOMS": 51,  # Unit number of support
        "V_MIN": 0.0,  # Minimum value of support
        "V_MAX": 200.0,  # Maximum value of support
    }

    # Define the connect four environment
    env = connect_four_v3.env()
    env.reset()

    # Configure the algo input arguments
    state_dim = [
        env.observation_space(agent)["observation"].shape for agent in env.agents
    ]
    one_hot = False
    action_dim = [env.action_space(agent).n for agent in env.agents]
    INIT_HP["DISCRETE_ACTIONS"] = True
    INIT_HP["MAX_ACTION"] = None
    INIT_HP["MIN_ACTION"] = None

    # Pre-process dimensions for pytorch layers
    # We will use self-play, so we only need to worry about the state dim of a single agent
    # We flatten the 6x7x2 observation as input to the agent's neural network
    state_dim = np.zeros(state_dim[0]).flatten().shape
    action_dim = action_dim[0]

    # Create a population ready for evolutionary hyper-parameter optimisation
    pop = initialPopulation(
        INIT_HP["ALGO"],
        state_dim,
        action_dim,
        one_hot,
        NET_CONFIG,
        INIT_HP,
        population_size=INIT_HP["POPULATION_SIZE"],
        device=device,
    )

    # Configure the replay buffer
    field_names = ["state", "action", "reward", "next_state", "done"]
    per = INIT_HP["PER"]
    n_step = True if INIT_HP["N_STEP"] > 1 else False
    if per:
        memory = PrioritizedReplayBuffer(
            action_dim,
            memory_size=INIT_HP["MEMORY_SIZE"],
            field_names=field_names,
            num_envs=2,
            alpha=INIT_HP["ALPHA"],
            gamma=INIT_HP["GAMMA"],
            device=device,
        )
        if n_step:
            n_step_memory = MultiStepReplayBuffer(
                action_dim,
                memory_size=INIT_HP["MEMORY_SIZE"],
                field_names=field_names,
                num_envs=2,
                n_step=INIT_HP["N_STEP"],
                gamma=INIT_HP["GAMMA"],
                device=device,
            )
    elif n_step:
        memory = MultiStepReplayBuffer(
            action_dim,
            memory_size=INIT_HP["MEMORY_SIZE"],
            field_names=field_names,
            num_envs=2,
            n_step=INIT_HP["N_STEP"],
            gamma=INIT_HP["GAMMA"],
            device=device,
        )
    else:
        memory = ReplayBuffer(
            action_dim=action_dim,  # Number of agent actions
            memory_size=INIT_HP["MEMORY_SIZE"],  # Max replay buffer size
            field_names=field_names,  # Field names to store in memory
            device=device,
        )

    # Instantiate a tournament selection object (used for HPO)
    tournament = TournamentSelection(
        tournament_size=2,  # Tournament selection size
        elitism=True,  # Elitism in tournament selection
        population_size=INIT_HP["POPULATION_SIZE"],  # Population size
        evo_step=1,
    )  # Evaluate using last N fitness scores

    # Instantiate a mutations object (used for HPO)
    mutations = Mutations(
        algo=INIT_HP["ALGO"],
        no_mutation=0.2,  # Probability of no mutation
        architecture=0.2,  # Probability of architecture mutation
        new_layer_prob=0.2,  # Probability of new layer mutation
        parameters=0.2,  # Probability of parameter mutation
        activation=0,  # Probability of activation function mutation
        rl_hp=0.2,  # Probability of RL hyperparameter mutation
        rl_hp_selection=[
            "lr",
            "learn_step",
            "batch_size",
        ],  # RL hyperparams selected for mutation
        mutation_sd=0.1,  # Mutation strength
        # Define search space for each hyperparameter
        min_lr=0.0001,
        max_lr=0.01,
        min_learn_step=1,
        max_learn_step=120,
        min_batch_size=8,
        max_batch_size=64,
        arch=NET_CONFIG["arch"],  # MLP or CNN
        rand_seed=1,
        device=device,
    )

    # Define training loop parameters
    episodes_per_epoch = 10
    max_episodes = 20000  # Total episodes
    max_steps = 500  # Maximum steps to take in each episode
    evo_epochs = 10  # Evolution frequency
    evo_loop = 50  # Number of evaluation episodes
    elite = pop[0]  # Assign a placeholder "elite" agent

    wandb.init(
        # set the wandb project where this run will be logged
        project="AgileRL",
        name="{}-EvoHPO-{}-RandomOpposition-{}".format(
            "connect_four_v3", INIT_HP["ALGO"], datetime.now().strftime("%m%d%Y%H%M%S")
        ),
        # track hyperparameters and run metadata
        config={
            "algo": "Evo HPO Rainbow DQN",
            "env": "connect_four_v3",
            "batch_size": INIT_HP["BATCH_SIZE"],
            "lr": INIT_HP["LR"],
            "gamma": INIT_HP["GAMMA"],
            "memory_size": INIT_HP["MEMORY_SIZE"],
            "learn_step": INIT_HP["LEARN_STEP"],
            "tau": INIT_HP["TAU"],
            "pop_size": INIT_HP["POPULATION_SIZE"],
        },
    )

    total_steps = 0
    pbar = trange(int(max_episodes / episodes_per_epoch))

    # Training loop
    for idx_epi in pbar:
        for agent in pop:  # Loop through population
            for episode in range(episodes_per_epoch):
                env.reset()  # Reset environment at start of episode
                observation, reward, done, truncation, _ = env.last()

                p1_state, p1_action, p1_next_state = None, None, None

                # Randomly decide whether agent will go first or second
                if random.random() > 0.5:
                    opponent_first = False
                else:
                    opponent_first = True

                score = 0

                for idx_step in range(max_steps):
                    # Player 0's turn
                    p0_action_mask = observation["action_mask"]
                    p0_state = observation["observation"]
                    p0_state = p0_state.flatten()
                    if opponent_first:
                        p0_action = env.action_space("player_0").sample(p0_action_mask)
                    else:
                        p0_action = agent.getAction(p0_state, p0_action_mask)[
                            0
                        ]  # Get next action from agent

                    env.step(p0_action)  # Act in environment
                    observation, reward, done, truncation, _ = env.last()
                    p0_next_state = observation["observation"]
                    p0_next_state = p0_next_state.flatten()

                    if not opponent_first:
                        score += reward

                    # Check if game is over (Player 0 win)
                    if done or truncation:
                        if per:
                            one_step_transition = n_step_memory.save2memoryVectEnvs(
                                [p0_state, p1_state],
                                [p0_action, p1_action],
                                [reward, -reward],
                                [p0_next_state, p1_next_state],
                                [done, done],
                            )
                            if one_step_transition:
                                memory.save2memoryVectEnvs(*one_step_transition)
                        else:
                            memory.save2memoryVectEnvs(
                                [p0_state, p1_state],
                                [p0_action, p1_action],
                                [reward, -reward],
                                [p0_next_state, p1_next_state],
                                [done, done],
                            )
                    else:
                        p0_reward = reward

                        # Player 1's turn
                        p1_action_mask = observation["action_mask"]
                        p1_state = observation["observation"]
                        p1_state[:, :, [0, 1]] = p1_state[:, :, [1, 0]]
                        p1_state = p1_state.flatten()
                        if not opponent_first:
                            p1_action = env.action_space("player_1").sample(
                                p1_action_mask
                            )
                        else:
                            p1_action = agent.getAction(p1_state, p1_action_mask)[
                                0
                            ]  # Get next action from agent

                        env.step(p1_action)  # Act in environment
                        observation, reward, done, truncation, _ = env.last()
                        p1_next_state = observation["observation"]
                        p1_next_state[:, :, [0, 1]] = p1_next_state[:, :, [1, 0]]
                        p1_next_state = p1_next_state.flatten()

                        if opponent_first:
                            score += reward

                        # Check if game is over (Player 1 win)
                        if done or truncation:
                            if per:
                                one_step_transition = n_step_memory.save2memoryVectEnvs(
                                    [p0_state, p1_state],
                                    [p0_action, p1_action],
                                    [-reward, reward],
                                    [p0_next_state, p1_next_state],
                                    [done, done],
                                )
                                if one_step_transition:
                                    memory.save2memoryVectEnvs(*one_step_transition)
                            else:
                                memory.save2memoryVectEnvs(
                                    [p0_state, p1_state],
                                    [p0_action, p1_action],
                                    [-reward, reward],
                                    [p0_next_state, p1_next_state],
                                    [done, done],
                                )

                        else:
                            if per:
                                one_step_transition = n_step_memory.save2memoryVectEnvs(
                                    [p0_state, p1_state],
                                    [p0_action, p1_action],
                                    [p0_reward, reward],
                                    [p0_next_state, p1_next_state],
                                    [done, done],
                                )
                                if one_step_transition:
                                    memory.save2memoryVectEnvs(*one_step_transition)
                            else:
                                memory.save2memoryVectEnvs(
                                    [p0_state, p1_state],
                                    [p0_action, p1_action],
                                    [p0_reward, reward],
                                    [p0_next_state, p1_next_state],
                                    [done, done],
                                )

                    if per:
                        fraction = min((idx_step + 1) / max_steps, 1.0)
                        agent.beta += fraction * (1.0 - agent.beta)

                    # Learn according to learning frequency
                    if (memory.counter % agent.learn_step == 0) and (
                        len(memory) >= agent.batch_size
                    ):
                        # Sample replay buffer
                        # Learn according to agent's RL algorithm
                        if per:
                            experiences = memory.sample(agent.batch_size, agent.beta)
                            if n_step_memory is not None:
                                n_step_experiences = n_step_memory.sample_from_indices(
                                    experiences[6]
                                )
                                experiences += n_step_experiences
                            idxs, priorities = agent.learn(
                                experiences, n_step=n_step, per=per
                            )
                            memory.update_priorities(idxs, priorities)
                        else:
                            experiences = memory.sample(agent.batch_size)
                            if n_step:
                                agent.learn(experiences, n_step=n_step)
                            else:
                                agent.learn(experiences)

                    # Stop episode if any agents have terminated
                    if done or truncation:
                        break

                total_steps += idx_step + 1

                # Save the total episode reward
                agent.scores.append(score)

        # Now evolve population if necessary
        if (idx_epi + 1) % evo_epochs == 0:
            # Evaluate population vs random actions
            fitnesses = []
            win_rates = []
            for agent in pop:
                with torch.no_grad():
                    rewards = []
                    for i in range(evo_loop):
                        env.reset()  # Reset environment at start of episode
                        observation, reward, done, truncation, _ = env.last()

                        player = -1  # Tracker for which player's turn it is

                        # Randomly decide whether agent will go first or second
                        if random.random() > 0.5:
                            opponent_first = False
                        else:
                            opponent_first = True

                        score = 0

                        for idx_step in range(max_steps):
                            action_mask = observation["action_mask"]
                            if player > 0:
                                if not opponent_first:
                                    action = env.action_space("player_1").sample(
                                        action_mask
                                    )
                                else:
                                    state = observation["observation"]
                                    state[:, :, [0, 1]] = state[:, :, [1, 0]]
                                    state = state.flatten()
                                    action = agent.getAction(state, action_mask)[
                                        0
                                    ]  # Get next action from agent
                            if player < 0:
                                if opponent_first:
                                    action = env.action_space("player_0").sample(
                                        action_mask
                                    )
                                else:
                                    state = observation["observation"]
                                    state = state.flatten()
                                    action = agent.getAction(state, action_mask)[
                                        0
                                    ]  # Get next action from agent

                            env.step(action)  # Act in environment
                            observation, reward, done, truncation, _ = env.last()

                            if (player > 0 and opponent_first) or (
                                player < 0 and not opponent_first
                            ):
                                score += reward

                            if done or truncation:
                                break

                            player *= -1

                        rewards.append(score)
                mean_fit = np.mean(rewards)
                agent.fitness.append(mean_fit)
                fitnesses.append(mean_fit)

            pbar.set_postfix_str(
                f"    Train Mean Score: {np.mean(agent.scores[-episodes_per_epoch:])}     Eval Mean Fitness: {np.mean(fitnesses)}     Eval Best Fitness: {np.max(fitnesses)}     Total Steps: {total_steps}"
            )
            pbar.update(0)

            wandb.log(
                {
                    "global_step": total_steps,
                    "train/mean_score": np.mean(agent.scores[-episodes_per_epoch:]),
                    "eval/mean_reward": np.mean(fitnesses),
                    "eval/best_fitness": np.max(fitnesses),
                }
            )

            # Tournament selection and population mutation
            # elite, pop = tournament.select(pop)
            # pop = mutations.mutation(pop)

    elite = pop[0]

    # Save the trained agent
    path = "./models/Rainbow_DQN"
    filename = "Rainbow_DQN_random_opp_trained_agent.pt"
    os.makedirs(path, exist_ok=True)
    save_path = os.path.join(path, filename)
    elite.saveCheckpoint(save_path)
