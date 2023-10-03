"""This tutorial shows how to train a DQN agent on the connect four environment.

Authors: Nick (https://github.com/nicku-a)
"""
import os
import random
from datetime import datetime

import numpy as np
import torch
import wandb
from agilerl.components.replay_buffer import ReplayBuffer
from agilerl.hpo.mutation import Mutations
from agilerl.hpo.tournament import TournamentSelection
from agilerl.utils.utils import initialPopulation
from tqdm import trange

from pettingzoo.classic import connect_four_v3

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("===== AgileRL Self-play Agent Demo - DQN =====")

    # Define the network configuration
    NET_CONFIG = {
        "arch": "mlp",  # Network architecture
        "h_size": [64, 64],  # Actor hidden size
    }

    # Define the initial hyperparameters
    INIT_HP = {
        "POPULATION_SIZE": 6,
        "ALGO": "DQN",  # Algorithm
        "DOUBLE": True,  # Use double Q-learning
        # Swap image channels dimension from last to first [H, W, C] -> [C, H, W]
        "BATCH_SIZE": 128,  # Batch size
        "LR": 1e-3,  # Learning rate
        "GAMMA": 0.99,  # Discount factor
        "MEMORY_SIZE": 10000,  # Max memory buffer size
        "LEARN_STEP": 2,  # Learning frequency
        "TAU": 0.01,  # For soft update of target parameters
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
    max_episodes = 2000  # Total episodes
    max_steps = 500  # Maximum steps to take in each episode
    epsilon = 1.0  # Starting epsilon value
    eps_end = 0.1  # Final epsilon value
    eps_decay = 0.995  # Epsilon decay
    evo_epochs = 20  # Evolution frequency
    evo_loop = 50  # Number of evaluation episodes
    elite = pop[0]  # Assign a placeholder "elite" agent

    wandb.init(
        # set the wandb project where this run will be logged
        project="AgileRL",
        name="{}-EvoHPO-{}-{}".format(
            "connect_four_v3", INIT_HP["ALGO"], datetime.now().strftime("%m%d%Y%H%M%S")
        ),
        # track hyperparameters and run metadata
        config={
            "algo": "Evo HPO DQN",
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
    pbar = trange(max_episodes)

    # Training loop
    for idx_epi in pbar:
        for agent in pop:  # Loop through population
            env.reset()  # Reset environment at start of episode
            observation, reward, done, truncation, _ = env.last()

            player = -1  # Tracker for which player's turn it is
            p1_score, p2_score = 0, 0  # Scores of player 1 and 2

            for idx_step in range(max_steps):
                if (
                    player > 0
                ):  # Flip the pieces so the agent always behaves as player 1
                    state = observation["observation"]
                    state[:, :, [0, 1]] = state[:, :, [1, 0]]
                    state = state.flatten()
                else:
                    state = observation["observation"].flatten()
                action_mask = observation["action_mask"]

                action = agent.getAction(state, epsilon, action_mask)[
                    0
                ]  # Get next action from agent
                env.step(action)  # Act in environment

                observation, reward, done, truncation, _ = env.last()

                if (
                    player > 0
                ):  # Again, flip the pieces so the agent has the perspective of player 1
                    p2_score += reward
                    next_state = observation["observation"]
                    next_state[:, :, [0, 1]] = next_state[:, :, [1, 0]]
                    next_state = next_state.flatten()
                else:
                    p1_score += reward
                    next_state = observation["observation"].flatten()
                next_action_mask = observation["action_mask"]

                # Save experiences to replay buffer
                memory.save2memory(state, action, reward, next_state, done)

                # Learn according to learning frequency
                if (memory.counter % agent.learn_step == 0) and (
                    len(memory) >= agent.batch_size
                ):
                    experiences = memory.sample(
                        agent.batch_size
                    )  # Sample replay buffer
                    agent.learn(experiences)  # Learn according to agent's RL algorithm

                # Stop episode if any agents have terminated
                if done or truncation:
                    break

                player *= -1  # Swap player for next turn

            total_steps += idx_step + 1

            # Save the total episode reward
            scores = (p1_score, p2_score)
            agent.scores.append(scores)

        # Update epsilon for exploration
        epsilon = max(eps_end, epsilon * eps_decay)

        # Now evolve population if necessary
        if (idx_epi + 1) % evo_epochs == 0:
            # Evaluate population vs random actions
            fitnesses = []
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
                                    action = agent.getAction(
                                        state, epsilon, action_mask
                                    )[
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
                                    action = agent.getAction(
                                        state, epsilon, action_mask
                                    )[
                                        0
                                    ]  # Get next action from agent

                            env.step(action)  # Act in environment
                            observation, reward, done, truncation, _ = env.last()

                            if (player > 0 and opponent_first) or (
                                player < 0 and not opponent_first
                            ):
                                score += reward
                            else:
                                score -= reward

                            if done or truncation:
                                break

                            player *= -1

                        rewards.append(score)
                mean_fit = np.mean(rewards)
                agent.fitness.append(mean_fit)
                fitnesses.append(mean_fit)

            fitness = ["%.2f" % fitness for fitness in fitnesses]
            avg_fitness = ["%.2f" % np.mean(agent.fitness[-100:]) for agent in pop]
            avg_score = ["%.2f" % np.mean(agent.scores[-100:]) for agent in pop]
            agents = [agent.index for agent in pop]
            num_steps = [agent.steps[-1] for agent in pop]
            muts = [agent.mut for agent in pop]
            pbar.update(0)

            print(
                f"""
                --- Epoch {idx_epi + 1} ---
                Fitness:\t\t{fitness}
                100 fitness avgs:\t{avg_fitness}
                100 score avgs:\t\t{avg_score}
                Agents:\t\t\t{agents}
                Steps:\t\t\t{num_steps}
                Mutations:\t\t\t{muts}
                """,
                end="\r",
            )

            wandb.log(
                {
                    "global_step": total_steps,
                    "eval/mean_fitness": np.mean(fitnesses),
                    "eval/best_fitness": np.max(fitnesses),
                }
            )

            # Tournament selection and population mutation
            elite, pop = tournament.select(pop)
            pop = mutations.mutation(pop)

    # Save the trained agent
    path = "./models/DQN"
    filename = "DQN_trained_agent.pt"
    os.makedirs(path, exist_ok=True)
    save_path = os.path.join(path, filename)
    elite.saveCheckpoint(save_path)
