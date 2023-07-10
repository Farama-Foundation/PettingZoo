"""Uses Stable-Baselines3 to train agents to play Knights-Archers-Zombies using SuperSuit vector envs.

This environment requires using SuperSuit's Black Death wrapper, to handle agent death.

For more information, see https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html

Author: Elliot (https://github.com/elliottower)
"""
from __future__ import annotations

import glob
import os
import time

import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy

from pettingzoo.butterfly import knights_archers_zombies_v10


def train(env_fn, steps: int = 10_000, seed: int | None = 0, **env_kwargs):
    # Train a single agent to play both sides in an AEC environment
    env = env_fn.parallel_env(**env_kwargs)

    env = ss.black_death_v3(env)

    # Convert into a Parallel environment in order to vectorize it (SuperSuit does not currently support vectorized AEC envs)
    # env = turn_based_aec_to_parallel(env)

    # Pre-process using SuperSuit (color reduction, resizing and frame stacking)
    # env = ss.color_reduction_v0(env, mode="B")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.frame_stack_v1(env, 3)

    # Add black death wrapper so the number of agents stays constant
    # MarkovVectorEnv does not support environments with varying numbers of active agents unless black_death is set to True

    env.reset(seed=seed)

    print(f"Starting training on {str(env.metadata['name'])}.")

    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, 8, num_cpus=2, base_class="stable_baselines3")

    # TODO: test different hyperparameters
    model = PPO(
        MlpPolicy,
        env,
        verbose=3,
        gamma=0.95,
        n_steps=256,
        ent_coef=0.0905168,
        learning_rate=0.00062211,
        vf_coef=0.042202,
        max_grad_norm=0.9,
        gae_lambda=0.99,
        n_epochs=5,
        clip_range=0.3,
        batch_size=256,
    )

    model.learn(total_timesteps=steps)

    model.save(f"{env.unwrapped.metadata.get('name')}_{time.strftime('%Y%m%d-%H%M%S')}")

    print("Model has been saved.")

    print(f"Finished training on {str(env.unwrapped.metadata['name'])}.")

    env.close()


def eval(env_fn, num_games: int = 100, render_mode: str | None = None, **env_kwargs):
    # Evaluate a trained agent vs a random agent
    env = env_fn.env(render_mode=render_mode, **env_kwargs)

    # Pre-process using SuperSuit (color reduction, resizing and frame stacking)
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.frame_stack_v1(env, 3)

    print(
        f"\nStarting evaluation on {str(env.metadata['name'])} (num_games={num_games}, render_mode={render_mode})"
    )

    try:
        latest_policy = max(
            glob.glob(f"{env.metadata['name']}*.zip"), key=os.path.getctime
        )
    except ValueError:
        print("Policy not found.")
        exit(0)

    model = PPO.load(latest_policy)

    rewards = {agent: 0 for agent in env.possible_agents}

    # TODO: figure out why Parallel performs differently at test time (my guess is maybe the way it counts num_cycles is different?)
    # # It seems to make the rewards worse, the same policy scores 2/3 points per archer vs 6/7 with AEC. n

    # from pettingzoo.utils.wrappers import RecordEpisodeStatistics
    #
    # env = env_fn.parallel_env(render_mode=render_mode, **env_kwargs)
    #
    # # Pre-process using SuperSuit (color reduction, resizing and frame stacking)
    # env = ss.resize_v1(env, x_size=84, y_size=84)
    # env = ss.frame_stack_v1(env, 3)
    # env = RecordEpisodeStatistics(env)
    #
    # stats = []
    # for i in range(num_games):
    #     observations, infos = env.reset(seed=i)
    #     done = False
    #     while not done:
    #         actions = {agent:  model.predict(observations[agent], deterministic=True)[0] for agent in env.agents}
    #         obss, rews, terms, truncs, infos = env.step(actions)
    #
    #         for agent in env.possible_agents:
    #             rewards[agent] += rews[agent]
    #         done = any(terms.values()) or any(truncs.values())
    #     stats.append(infos["episode"])

    # Note: we evaluate here using an AEC environments, to allow for easy A/B testing against random policies
    # For example, we can see here that using a random agent for archer_0 results in less points than the trained agent
    for i in range(num_games):
        env.reset(seed=i)
        env.action_space(env.possible_agents[0]).seed(i)

        for agent in env.agent_iter():
            obs, reward, termination, truncation, info = env.last()

            for agent in env.agents:
                rewards[agent] += env.rewards[agent]

            if termination or truncation:
                break
            else:
                if agent == env.possible_agents[0]:
                    act = env.action_space(agent).sample()
                else:
                    act = model.predict(obs, deterministic=True)[0]
            env.step(act)
    env.close()

    avg_reward = sum(rewards.values()) / len(rewards.values())
    avg_reward_per_agent = {
        agent: rewards[agent] / num_games for agent in env.possible_agents
    }
    print(f"Avg reward: {avg_reward}")
    print("Avg reward per agent, per game: ", avg_reward_per_agent)
    print("Full rewards: ", rewards)
    return avg_reward


if __name__ == "__main__":
    env_fn = knights_archers_zombies_v10

    # TODO: test out more hyperparameter combos
    # max_cycles 100, max zombies 4, 8192 * 10 works decently, but sometimes fails due to agents dying
    # black death wrapper, max cycles 100, max zombies 4, 8192*10, seems to work well (13 points over 10 games)
    # black death wrapper, max_cycles 900 (default) allowed the knights to get kills 1/10 games, but worse archer performance (6 points)

    env_kwargs = dict(max_cycles=100, max_zombies=4)

    # Train a model (takes ~5 minutes on a laptop CPU)
    train(env_fn, steps=8192*10, seed=0, **env_kwargs)

    # Evaluate 10 games (takes ~10 seconds on a laptop CPU)
    eval(env_fn, num_games=10, render_mode=None, **env_kwargs)

    # Watch 2 games (takes ~10 seconds on a laptop CPU)
    eval(env_fn, num_games=2, render_mode="human", **env_kwargs)
