import gym
import random
import numpy as np

import ray
from ray import tune
from ray.rllib.models import Model, ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.utils import try_import_tf
from gamma_games.piston_ball import piston_ball
from gamma_games.cooperative_pong import cooperative_pong
from sisl_games.pursuit import pursuit

tf = try_import_tf()


class CustomModel1(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        last_layer = tf.layers.dense(
                input_dict["obs"], 400, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(
            last_layer, 300, activation=tf.nn.relu, name="fc2")
        output = tf.layers.dense(
            last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer


if __name__ == "__main__":
    ray.init()

    # Simple environment with `num_agents` independent cartpole entities
    ModelCatalog.register_custom_model("model1", CustomModel1)

    # pursuit

    def env_creator(args):
        return pursuit.env()

    env = env_creator(1)
    register_env("pursuit", env_creator)

    obs_space = gym.spaces.Box(low=0, high=1, shape=(148,), dtype=np.float32)
    act_space = gym.spaces.Discrete(5)

    """
    # cooperative pong

    def env_creator(args):
        return cooperative_pong.env()

    env = env_creator(1)
    register_env("cooperative_pong", env_creator)

    obs_space = gym.spaces.Box(low=0, high=255, shape=(flattened_shape,), dtype=np.uint8)
    act_space = gym.spaces.Discrete(3)
    """

    """
    # pistonball
    def env_creator(args):
        return piston_ball.env()

    env = env_creator(1)
    register_env("pistonBall", env_creator)

    obs_space = gym.spaces.Box(low=0, high=255, shape=(1500,), dtype=np.uint8)
    act_space = gym.spaces.Discrete(3)
    """

    # Each policy can have a different configuration (including custom model)
    def gen_policy(i):
        config = {
            "model": {
                "custom_model": "model1",
            },
            "gamma": 0.99,
        }
        return (None, obs_space, act_space, config)

    # Setup PPO with an ensemble of `num_policies` different policies
    policies = {
        "policy_{}".format(i): gen_policy(i)
        for i in range(1)
    }
    policy_ids = list(policies.keys())

    tune.run(
        "DQN",
        stop={"episodes_total": 60000},
        checkpoint_freq=100,
        config={

            # Enviroment specific
            "env": "pursuit",

            # General
            "log_level": "ERROR",
            "num_gpus": 1,
            "num_workers": 8,
            "num_envs_per_worker": 8,
            "learning_starts": 1000,
            "buffer_size": int(1e5),
            "compress_observations": True,
            "sample_batch_size": 20,
            "train_batch_size": 512,
            "gamma": .99,

            # Method specific

            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id: policy_ids[0]),
            },
        },
    )


"""
    tune.run(
        "APEX",
        stop={"episodes_total": 60000},
        checkpoint_freq=100,
        config={
            "env": "pistonBall",
            "log_level": "ERROR",

            "num_gpus": 1,
            "num_workers": 8,
            "num_envs_per_worker": 8,

            "buffer_size": int(1e5),
            "compress_observations": True,

            "double_q": False,
            "dueling": False,
            "num_atoms": 1,
            "noisy": False,
            "n_step": 3,
            "lr": .0001,
            "adam_epsilon": .00015,
            "hiddens": [512],
            "schedule_max_timesteps": 60000,
            "exploration_final_eps": 0.01,
            "exploration_fraction": .1,
            "prioritized_replay_alpha": 0.5,
            "beta_annealing_fraction": 1.0,
            "final_prioritized_replay_beta": 1.0,

            "sample_batch_size": 20,
            "train_batch_size": 512,
            "target_network_update_freq": 50000,
            "timesteps_per_iteration": 25000,

            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id: policy_ids[0]),
            },
        },
    )
"""
