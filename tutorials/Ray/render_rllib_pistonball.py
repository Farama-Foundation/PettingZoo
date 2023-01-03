"""Uses Ray's RLLib to view trained agents playing Pistonball.

Author: Rohan (https://github.com/Rohan138)
"""

import argparse
import os
from pathlib import Path

import pickle5 as pickle
import ray
import supersuit as ss
from PIL import Image
from ray.rllib.algorithms.ppo import PPO
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env

from pettingzoo.butterfly import pistonball_v6
from tutorials.Ray.rllib_pistonball import CNNModelV2

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

ModelCatalog.register_custom_model("CNNModelV2", CNNModelV2)


def env_creator():
    env = pistonball_v6.env(
        n_pistons=20,
        time_penalty=-0.1,
        continuous=True,
        random_drop=True,
        random_rotate=True,
        ball_mass=0.75,
        ball_friction=0.3,
        ball_elasticity=1.5,
        max_cycles=125,
        render_mode="rgb_array",
    )
    env = ss.color_reduction_v0(env, mode="B")
    env = ss.dtype_v0(env, "float32")
    env = ss.resize_v1(env, x_size=84, y_size=84)
    env = ss.normalize_obs_v0(env, env_min=0, env_max=1)
    env = ss.frame_stack_v1(env, 3)
    return env


env = env_creator()
env_name = "pistonball_v6"
register_env(env_name, lambda config: PettingZooEnv(env_creator()))

with open(params_path, "rb") as f:
    config = pickle.load(f)
    # num_workers not needed since we are not training
    del config["num_workers"]
    del config["num_gpus"]

ray.init(num_cpus=8, num_gpus=1)
PPOagent = PPO(env=env_name, config=config)
PPOagent.restore(checkpoint_path)


reward_sum = 0
frame_list = []
i = 0
env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    reward_sum += reward
    if termination or truncation:
        action = None
    else:
        action, _, _ = PPOagent.get_policy("policy_0").compute_single_action(
            observation
        )

    env.step(action)
    i += 1
    if i % (len(env.possible_agents) + 1) == 0:
        img = Image.fromarray(env.render())
        frame_list.append(img)
env.close()


print(reward_sum)
frame_list[0].save(
    "out.gif", save_all=True, append_images=frame_list[1:], duration=3, loop=0
)
