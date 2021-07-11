"""
This script trains a PettingZoo MPE environment with continuous action
spaces using RLlib's implementation of MADDPG.
Note that the PettingZoo's MPE environments are not directly comparable to the 
original OpenAI MPE environments due to minor changes and bug fixes.
"""

import ray
from ray import tune
from ray.tune.registry import register_trainable, register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
import ray.rllib.contrib.maddpg.maddpg as maddpg
from pettingzoo.mpe import *
import supersuit as ss
import argparse
from importlib import import_module
from ray.tune import CLIReporter
import os

def parse_args():
    # Environment
    parser = argparse.ArgumentParser("RLLib MADDPG with PettingZoo environments")

    parser.add_argument(
        "--env-type",
        choices=["mpe", "sisl", "atari", "butterfly", "classic", "magent"],
        default="mpe",
        help="The PettingZoo environment type"
    )
    parser.add_argument(
        "--env-name",
        type=str,
        default="simple_spread_v2",
        help="The PettingZoo environment to use"
    )
    parser.add_argument("--max-episode-len", type=int, default=25,
                        help="maximum episode length")
    parser.add_argument("--num-episodes", type=int, default=60000,
                        help="number of episodes")
    parser.add_argument("--num-adversaries", type=int, default=0,
                        help="number of adversaries")
    parser.add_argument("--good-policy", type=str, default="maddpg",
                        help="policy for good agents")
    parser.add_argument("--adv-policy", type=str, default="maddpg",
                        help="policy of adversaries")

    # Core training parameters
    parser.add_argument("--lr", type=float, default=1e-2,
                        help="learning rate for Adam optimizer")
    parser.add_argument("--gamma", type=float, default=0.95,
                        help="discount factor")
    parser.add_argument("--rollout-fragment-length", type=int, default=25,
                        help="number of data points sampled /update /worker")
    parser.add_argument("--train-batch-size", type=int, default=1024,
                        help="number of data points /update")
    parser.add_argument("--n-step", type=int, default=1,
                        help="length of multistep value backup")
    parser.add_argument("--num-units", type=int, default=64,
                        help="number of units in the mlp")
    parser.add_argument("--replay-buffer", type=int, default=1000000,
                        help="size of replay buffer in training")

    # Checkpoint
    parser.add_argument("--checkpoint-freq", type=int, default=10000,
                        help="save model once every time this many iterations are completed")
    parser.add_argument("--local-dir", type=str, default="~/ray_results",
                        help="path to save checkpoints")
    parser.add_argument("--restore", type=str, default=None,
                        help="directory in which training state and model are loaded")

    # Parallelism
    parser.add_argument("--num-workers", type=int, default=1)
    parser.add_argument("--num-envs-per-worker", type=int, default=4)
    parser.add_argument("--num-gpus", type=int, default=0)

    # Evaluation
    parser.add_argument("--eval-freq", type=int, default=0,
                        help="evaluate model every time this many iterations are completed")
    parser.add_argument("--eval-num-episodes", type=int, default=5,
                        help="Number of episodes to run for evaluation")
    parser.add_argument("--render", type=bool, default=False,
                        help="render environment for evaluation")
    parser.add_argument("--record", type=str, default=None,
                        help="path to store evaluation videos")
    return parser.parse_args()


def main(args):
    ray.init()
    MADDPGAgent = maddpg.MADDPGTrainer
    register_trainable("MADDPG", MADDPGAgent)
    env_name = args.env_name
    env_str = "pettingzoo." + args.env_type + "." + env_name

    def env_creator(config):
        env = import_module(env_str)
        env = env.parallel_env(max_cycles=args.max_episode_len, continuous_actions=True)
        env = ss.pad_observations_v0(env)
        env = ss.pad_action_space_v0(env)
        return env

    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))

    env = ParallelPettingZooEnv(env_creator(args))
    obs_space = env.observation_spaces
    act_space = env.action_spaces
    print("observation spaces: ", obs_space)
    print("action spaces: ", act_space)
    agents = env.agents

    def gen_policy(i):
        use_local_critic = [
            args.adv_policy == "ddpg" if i < args.num_adversaries else
            args.good_policy == "ddpg" for i in range(len(env.agents))
        ]
        return (
            None,
            env.observation_spaces[agents[i]],
            env.action_spaces[agents[i]],
            {
                "agent_id": i,
                "use_local_critic": use_local_critic[i],
            }
        )

    policies = {"policy_%d" %i: gen_policy(i) for i in range(len(env.agents))}
    policy_ids = list(policies.keys())

    config={
            # === Setup ===
            "log_level": "ERROR",
            "env": env_name,
            "num_workers": args.num_workers,
            "num_gpus": args.num_gpus,
            "num_gpus_per_worker": 0,
            "num_envs_per_worker": args.num_envs_per_worker,
            "horizon": args.max_episode_len,

            # === Policy Config ===
            # --- Model ---
            "good_policy": args.good_policy,
            "adv_policy": args.adv_policy,
            "actor_hiddens": [args.num_units] * 2,
            "actor_hidden_activation": "relu",
            "critic_hiddens": [args.num_units] * 2,
            "critic_hidden_activation": "relu",
            "n_step": args.n_step,
            "gamma": args.gamma,

            # --- Exploration ---
            "tau": 0.01,

            # --- Replay buffer ---
            "buffer_size": args.replay_buffer,

            # --- Optimization ---
            "actor_lr": args.lr,
            "critic_lr": args.lr,
            "learning_starts": args.train_batch_size * args.max_episode_len,
            "rollout_fragment_length": args.rollout_fragment_length,
            "train_batch_size": args.train_batch_size,
            "batch_mode": "truncate_episodes",

            # === Multi-agent setting ===
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": lambda name: policy_ids[agents.index(name)],
                # Workaround because MADDPG requires agent_id: int but actual ids are strings like 'speaker_0'
            },
    
            # === Evaluation and rendering ===
            "evaluation_interval": args.eval_freq,
            "evaluation_num_episodes": args.eval_num_episodes,
            "evaluation_config": {
                "record_env": args.record,
                "render_env": args.render,
            },
        }
    
    tune.run(
        "contrib/MADDPG",
        name="PZ_MADDPG",
        config=config,
        progress_reporter=CLIReporter(),
        stop={
            "episodes_total": args.num_episodes,
        },
        checkpoint_freq=args.checkpoint_freq,
        local_dir=os.path.join(args.local_dir, args.env_name),
        restore=args.restore,
        verbose = 2
    )


if __name__ == '__main__':
    args = parse_args()
    main(args)
