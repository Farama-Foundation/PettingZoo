from sisl_games.waterworld.waterworld import env as custom_env
import ray
from ray.tune.registry import register_trainable, register_env
import ray.rllib.agents.dqn as dqn
import ray.rllib.agents.ddpg.td3 as td3
import os
import pickle
import numpy as np
from ray.rllib.models import ModelCatalog
# from parameterSharingWWorld import MLPModel

env_name = "waterworld"
# path should end with checkpoint-<> data file
checkpoint_path = "/home/ananth/ray_results/TD3/TD3_waterworld_20cc0cbc_2020-02-05_15-00-16w7onxvxh/checkpoint_23450/checkpoint-23450"

# TODO: see ray/rllib/rollout.py -- `run` method for checkpoint restoring

# register env -- For some reason, ray is unable to use already registered env in config
def env_creator(args):
    return custom_env()

env = env_creator(1)
register_env(env_name, env_creator)

# get the config file - params.pkl
config_path = os.path.dirname(checkpoint_path)
config_path = os.path.join(config_path, "../params.pkl")
with open(config_path, "rb") as f:
    config = pickle.load(f)


# ModelCatalog.register_custom_model("MLPModel", MLPModel)

print(env.observation_space_dict)
# exit()

ray.init()
TD3Agent = td3.TD3Trainer(env=env_name, config=config)
TD3Agent.restore(checkpoint_path)

# init obs, action, reward
observations = env.reset()
rewards, action_dict = {}, {}
for agent_id in env.agent_ids:
    assert isinstance(agent_id, int), "Error: agent_ids are not ints."
    # action_dict = dict(zip(env.agent_ids, [np.array([0,1,0]) for _ in range(len(env.agent_ids))]))  # no action = [0,1,0]
    action_dict = dict(zip(env.agent_ids, [env.action_space_dict[i].sample() for i in env.agent_ids]))
    rewards[agent_id] = 0

totalReward = 0
done = False
# action_space_len = 3 # for all agents

# TODO: extra parameters : /home/ananth/miniconda3/envs/maddpg/lib/python3.7/site-packages/ray/rllib/policy/policy.py

while not done:
    action_dict = {}
    # compute_action does not cut it. Go to the policy directly
    for agent_id in env.agent_ids:
        # print("id {}, obs {}, rew {}".format(agent_id, observations[agent_id], rewards[agent_id]))
        action, _, _ = TD3Agent.get_policy("policy_0").compute_single_action(observations[agent_id], prev_reward=rewards[agent_id]) # prev_action=action_dict[agent_id]
        # print(action)
        action_dict[agent_id] = action

    observations, rewards, dones, info = env.step(action_dict)
    env.render()
    totalReward += rewards[0]
    done = any(list(dones.values()))

env.close()

print("done", done, totalReward)
