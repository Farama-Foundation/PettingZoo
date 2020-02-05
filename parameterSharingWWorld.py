import gym
import random
import numpy as np

import ray
from ray import tune
from ray.rllib.models import Model, ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.utils import try_import_tf
from sisl_games.pursuit import pursuit
from sisl_games.multi_walker import multi_walker
from sisl_games.waterworld import waterworld

tf = try_import_tf()


class MLPModel(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        last_layer = tf.layers.dense(
                input_dict["obs"], 400, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(
            last_layer, 300, activation=tf.nn.relu, name="fc2")
        output = tf.layers.dense(
            last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer


# ray.init()

ModelCatalog.register_custom_model("MLPModel", MLPModel)


# waterworld
def env_creator(args):
    return waterworld.env()

env = env_creator(1)
register_env("waterworld", env_creator)

"""
# multi_walker
def env_creator(args):
    return multi_walker.env()

env = env_creator(1)
register_env("multi_walker", env_creator)

# cooperative pong
def env_creator(args):
    return cooperative_pong.env()

env = env_creator(1)
register_env("cooperative_pong", env_creator)

obs_space = gym.spaces.Box(low=0, high=255, shape=(flattened_shape,), dtype=np.uint8)
act_space = gym.spaces.Discrete(3)

# pistonball
def env_creator(args):
    return piston_ball.env()

env = env_creator(1)
register_env("pistonBall", env_creator)

obs_space = gym.spaces.Box(low=0, high=255, shape=(1500,), dtype=np.uint8)
act_space = gym.spaces.Discrete(3)
"""

obs_space = env.observation_space_dict[0]
act_space = env.action_space_dict[0]

def gen_policy(i):
    config = {
        "model": {
            "custom_model": "MLPModel",
        },
        "gamma": 0.99,
    }
    return (None, obs_space, act_space, config)


policies = {"policy_0": gen_policy(0)}
policy_ids = list(policies.keys())

# DQN and Apex-DQN do not work with continuous actions

"""
tune.run(
    "PPO",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

        # General
        "log_level": "ERROR",
        "num_gpus": 1,
        "num_workers": 8,
        "num_envs_per_worker": 8,
        "compress_observations": False,
        "gamma": .99,


        "lambda": 0.95,
        "kl_coeff": 0.5,
        "clip_rewards": True,
        "clip_param": 0.1,
        "vf_clip_param": 10.0,
        "entropy_coeff": 0.01,
        "train_batch_size": 5000,
        "sample_batch_size": 100,
        "sgd_minibatch_size": 500,
        "num_sgd_iter": 10,
        "batch_mode": 'truncate_episodes',
        "vf_share_layers": True,

        # Method specific

        "multiagent": {
            "policies": policies,
            "policy_mapping_fn": (
                lambda agent_id: policy_ids[0]),
        },
    },
)
"""

"""
tune.run(
    "IMPALA",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

        # General
        "log_level": "ERROR",
        "num_gpus": 1,
        "num_workers": 8,
        "num_envs_per_worker": 8,
        "compress_observations": True,
        "sample_batch_size": 20,
        "train_batch_size": 512,
        "gamma": .99,

        "clip_rewards": True,
        "lr_schedule": [[0, 0.0005],[20000000, 0.000000000001]],

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
    "A2C",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

        # General
        "log_level": "ERROR",
        "num_gpus": 1,
        "num_workers": 8,
        "num_envs_per_worker": 8,
        "compress_observations": False,
        "sample_batch_size": 20,
        "train_batch_size": 512,
        "gamma": .99,

        "lr_schedule": [[0, 0.0007],[20000000, 0.000000000001]],

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
    "APEX_DDPG",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

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

        "n_step": 3,
        "lr": .0001,
        "exploration_fraction": .1,
        "prioritized_replay_alpha": 0.5,
        "beta_annealing_fraction": 1.0,
        "final_prioritized_replay_beta": 1.0,
        "target_network_update_freq": 50000,
        "timesteps_per_iteration": 25000,

        # Method specific

        "multiagent": {
            "policies": policies,
            "policy_mapping_fn": (
                lambda agent_id: policy_ids[0]),
        },
    },
)
"""

"""
tune.run(
    "TD3",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

        # General
        "log_level": "ERROR",
        "num_gpus": 1,
        "num_workers": 8,
        "num_envs_per_worker": 8,
        "learning_starts": 5000,
        "buffer_size": int(1e5),
        "compress_observations": True,
        "sample_batch_size": 20,
        "train_batch_size": 512,
        "gamma": .99,

        "critic_hiddens": [256, 256],
        "pure_exploration_steps": 5000,

        # Method specific

        "multiagent": {
            "policies": policies,
            "policy_mapping_fn": (
                lambda agent_id: policy_ids[0]),
        },
    },
)
"""

"""
tune.run(
    "SAC",
    stop={"episodes_total": 60000},
    checkpoint_freq=10,
    config={

        # Enviroment specific
        "env": "waterworld",

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

        "horizon": 200,
        "soft_horizon": False,
        "Q_model": {
          "hidden_activation": "relu",
          "hidden_layer_sizes": [256, 256]
          },
        "tau": 0.005,
        "target_entropy": "auto",
        "no_done_at_end": True,
        "n_step": 1,
        "prioritized_replay": False,
        "target_network_update_freq": 1,
        "timesteps_per_iteration": 1000,
        "exploration_enabled": True,
        "optimization": {
          "actor_learning_rate": 0.0003,
          "critic_learning_rate": 0.0003,
          "entropy_learning_rate": 0.0003,
          },
        "clip_actions": False,
        #TODO -- True
        "normalize_actions": False,
        "evaluation_interval": 1,
        "metrics_smoothing_episodes": 5,

        "multiagent": {
            "policies": policies,
            "policy_mapping_fn": (
                lambda agent_id: policy_ids[0]),
        },
    },
)
"""
