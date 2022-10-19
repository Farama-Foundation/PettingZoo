"""Uses Ray's RLLib to view trained agents playing Leduoc Holdem.

Author: Rohan (https://github.com/Rohan138)
"""

import argparse
import os
import pickle
from pathlib import Path

import numpy as np
import ray
from ray.rllib.algorithms.dqn import DQN, DQNConfig
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from rllib_leduc_holdem import TorchMaskedActions

from pettingzoo.classic import leduc_holdem_v4

raise NotImplementedError(
    "There are currently bugs in this tutorial, we will fix them soon."
)

os.environ["SDL_VIDEODRIVER"] = "dummy"

parser = argparse.ArgumentParser(
    description="Render pretrained policy loaded from checkpoint"
)
parser.add_argument(
    "checkpoint_path",
    help="Path to the checkpoint. This path will likely be something like this: `~/ray_results/pistonball_v6/PPO/PPO_pistonball_v6_660ce_00000_0_2021-06-11_12-30-57/checkpoint_000050/checkpoint-50`",
)

args = parser.parse_args()

checkpoint_path = os.path.expanduser(args.checkpoint_path)
params_path = Path(checkpoint_path).parent.parent / "params.pkl"


alg_name = "DQN"
ModelCatalog.register_custom_model("pa_model", TorchMaskedActions)
# function that outputs the environment you wish to register.


def env_creator():
    env = leduc_holdem_v4.env()
    return env


num_cpus = 1

config = DQNConfig().to_dict()

register_env("leduc_holdem", lambda config: PettingZooEnv(env_creator()))

env = env_creator()

with open(params_path, "rb") as f:
    config = pickle.load(f)
    # num_workers not needed since we are not training
    del config["num_workers"]
    del config["num_gpus"]

ray.init(num_cpus=8, num_gpus=0)
DQNAgent = DQN(env="leduc_holdem", config=config)
DQNAgent.restore(checkpoint_path)

reward_sums = {a: 0 for a in env.possible_agents}
i = 0
env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    obs = observation["observation"]
    reward_sums[agent] += reward
    if termination or truncation:
        action = None
    else:
        print(DQNAgent.get_policy(agent))
        policy = DQNAgent.get_policy(agent)
        batch_obs = {
            "obs": {
                "observation": np.expand_dims(observation["observation"], 0),
                "action_mask": np.expand_dims(observation["action_mask"], 0),
            }
        }
        batched_action, state_out, info = policy.compute_actions_from_input_dict(
            batch_obs
        )
        single_action = batched_action[0]
        action = single_action

    env.step(action)
    i += 1
    env.render()

print("rewards:")
print(reward_sums)
