"""Uses Ray's RLlib to view trained agents playing Pistonball.

Author: Rohan (https://github.com/Rohan138)
"""

import argparse
import os

import ray
import supersuit as ss
from PIL import Image
from ray.rllib.algorithms.ppo import PPO
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.tune.registry import register_env
from torch import nn

from pettingzoo.butterfly import pistonball_v6


class CNNModelV2(TorchModelV2, nn.Module):
    def __init__(self, obs_space, act_space, num_outputs, *args, **kwargs):
        TorchModelV2.__init__(self, obs_space, act_space, num_outputs, *args, **kwargs)
        nn.Module.__init__(self)
        self.model = nn.Sequential(
            nn.Conv2d(3, 32, [8, 8], stride=(4, 4)),
            nn.ReLU(),
            nn.Conv2d(32, 64, [4, 4], stride=(2, 2)),
            nn.ReLU(),
            nn.Conv2d(64, 64, [3, 3], stride=(1, 1)),
            nn.ReLU(),
            nn.Flatten(),
            (nn.Linear(3136, 512)),
            nn.ReLU(),
        )
        self.policy_fn = nn.Linear(512, num_outputs)
        self.value_fn = nn.Linear(512, 1)

    def forward(self, input_dict, state, seq_lens):
        model_out = self.model(input_dict["obs"].permute(0, 3, 1, 2))
        self._value_out = self.value_fn(model_out)
        return self.policy_fn(model_out), state

    def value_function(self):
        return self._value_out.flatten()


os.environ["SDL_VIDEODRIVER"] = "dummy"

parser = argparse.ArgumentParser(
    description="Render pretrained policy loaded from checkpoint"
)
parser.add_argument(
    "--checkpoint-path",
    help="Path to the checkpoint. This path will likely be something like this: `~/ray_results/pistonball_v6/PPO/PPO_pistonball_v6_660ce_00000_0_2021-06-11_12-30-57/checkpoint_000050/checkpoint-50`",
)

args = parser.parse_args()

if args.checkpoint_path is None:
    print("The following arguments are required: --checkpoint-path")
    exit(0)

checkpoint_path = os.path.expanduser(args.checkpoint_path)

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


ray.init()

PPOagent = PPO.from_checkpoint(checkpoint_path)

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
        action = PPOagent.compute_single_action(observation)

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
