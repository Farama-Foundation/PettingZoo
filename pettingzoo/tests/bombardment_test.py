from .api_test import test_observation
import random
from copy import copy


def bombardment_test(env, cycles=10000):
    print("Starting bombardment test")

    prev_observe = env.reset()
    observation_0 = copy(prev_observe)
    for i in range(cycles):
        if i == cycles / 2:
            print("\t50% through bombardment test")
        for agent in env.agent_iter(env.num_agents):  # step through every agent once with observe=True
            reward, done, info = env.last()
            if not done and 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            next_observe = env.step(action)
            assert env.observation_spaces[agent].contains(prev_observe), "Agent's observation is outside of its observation space"
            test_observation(prev_observe, observation_0)
            prev_observe = next_observe
        prev_observe = env.reset()
    print("Passed bombardment test")
