"""Uses Ray's RLlib to train agents to play Pistonball.

Author: Rohan (https://github.com/Rohan138)
"""

import os
from pathlib import Path

import ray
import supersuit as ss
from ray import tune
from ray.rllib.algorithms.ppo import PPO, PPOConfig
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env

from pettingzoo import make

# Conv stack applied to each agent's (84, 84, 3) observation, as
# [num_out_channels, kernel, stride] triples. The final 7x7 layer collapses the
# 7x7x64 feature map into a 512-wide vector, which the policy and value heads
# read from.
CONV_FILTERS = [[32, 8, 4], [64, 4, 2], [64, 3, 1], [512, 7, 1]]


def env_creator(args):
    env = make(
        "parallel",
        "butterfly/pistonball-v6",
        n_pistons=20,
        time_penalty=-0.1,
        continuous=True,
        random_drop=True,
        random_rotate=True,
        ball_mass=0.75,
        ball_friction=0.3,
        ball_elasticity=1.5,
        max_cycles=125,
    )
    env = ss.color_reduction_v0(env, mode="B")
    env = ss.dtype_v0(env, "float32")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.normalize_obs_v0(env, env_min=0, env_max=1)
    env = ss.frame_stack_v1(env, 3)
    return env


if __name__ == "__main__":
    ray.init()

    env_name = "pistonball_v6"

    def _make_rllib_env(config):
        base = env_creator(config)
        wrapped = ParallelPettingZooEnv(base)
        wrapped._agent_ids = set(getattr(base, "possible_agents", []))
        return wrapped

    register_env(env_name, _make_rllib_env)

    config = (
        PPOConfig()
        .environment(
            env=env_name,
            clip_actions=True,
            disable_env_checking=True,
        )
        # Every piston shares one policy. Without this, RLlib treats the env as
        # single-agent and tries to build one encoder over the full
        # Dict(piston_0, ..., piston_19) observation space.
        .multi_agent(
            policies={"shared_policy"},
            policy_mapping_fn=lambda agent_id, *args, **kwargs: "shared_policy",
        )
        .rl_module(model_config=DefaultModelConfig(conv_filters=CONV_FILTERS))
        .env_runners(num_env_runners=4, rollout_fragment_length=128)
        .training(
            train_batch_size=512,
            lr=2e-5,
            gamma=0.99,
            lambda_=0.9,
            use_gae=True,
            clip_param=0.4,
            grad_clip=None,
            entropy_coeff=0.1,
            vf_loss_coeff=0.25,
            minibatch_size=64,
            num_epochs=10,
        )
        .debugging(log_level="ERROR")
        .framework(framework="torch")
        .learners(num_gpus_per_learner=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
    )

    storage_uri = (Path("~/ray_results") / env_name).expanduser().resolve().as_uri()

    tune.run(
        PPO,
        name="PPO",
        stop={"timesteps_total": 5000000 if not os.environ.get("CI") else 50000},
        checkpoint_freq=10,
        storage_path=storage_uri,
        config=config.to_dict(),
    )
