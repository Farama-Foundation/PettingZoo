"""This is a minimal example to show how to use Tianshou with a PettingZoo environment. No training of agents is done here.

Author: Will (https://github.com/WillDudley)

Python version used: 3.8.10

Requirements:
pettingzoo == 1.22.0
git+https://github.com/thu-ml/tianshou
"""

from tianshou.data import Collector
from tianshou.env import DummyVectorEnv, PettingZooEnv
from tianshou.policy import MultiAgentPolicyManager, RandomPolicy

from pettingzoo.classic import rps_v2

if __name__ == "__main__":
    # Step 1: Load the PettingZoo environment
    env = rps_v2.env(render_mode="human")

    # Step 2: Wrap the environment for Tianshou interfacing
    env = PettingZooEnv(env)

    # Step 3: Define policies for each agent
    policies = MultiAgentPolicyManager([RandomPolicy(), RandomPolicy()], env)

    # Step 4: Convert the env to vector format
    env = DummyVectorEnv([lambda: env])

    # Step 5: Construct the Collector, which interfaces the policies with the vectorised environment
    collector = Collector(policies, env)

    # Step 6: Execute the environment with the agents playing for 1 episode, and render a frame every 0.1 seconds
    result = collector.collect(n_episode=1, render=0.1)
