from .api_test import test_obervation
import random


def bombardment_test(env):
    print("Starting bombardment test")
    cycles = 10000

    prev_observe = env.reset()
    observation_0 = prev_observe.copy()
    for _ in range(cycles):
        for agent in env.agent_order:  # step through every agent once with observe=True
            if 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            next_observe = env.step(action)
            assert env.observation_spaces[agent].contains(prev_observe), "Agent's observation is outside of its observation space"
            test_obervation(prev_observe, observation_0)
            prev_observe = next_observe
            if all(env.dones.values()):
                prev_observe = env.reset()
                break
    print("Passed bombardment test")
