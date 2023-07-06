"""Uses Stable-Baselines3 to train agents to play Rock-Paper-Scissors.

Adapted from https://towardsdatascience.com/multi-agent-deep-reinforcement-learning-in-15-lines-of-code-using-pettingzoo-e0b963c0820b

Authors: Jordan (https://github.com/jkterry1), Elliot (https://github.com/elliottower)
"""
import time

import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy

from pettingzoo.classic import rps_v2
from pettingzoo.utils import turn_based_aec_to_parallel

env = rps_v2.env()
env = turn_based_aec_to_parallel(env)

env = ss.pettingzoo_env_to_vec_env_v1(env)
env = ss.concat_vec_envs_v1(env, 8, num_cpus=4, base_class="stable_baselines3")

# TODO: find hyperparameters that make the model actually learn
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

model.learn(total_timesteps=2_000_000)

model.save(f"{env.unwrapped.metadata.get('name')}_{time.strftime('%Y%m%d-%H%M%S')}")

print("Model has been saved.")
