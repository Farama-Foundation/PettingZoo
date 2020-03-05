import pettingzoo
import warnings
import numpy as np


def test_obervation(observation):
    if not isinstance(observation, np.ndarray):
        warnings.warn("Observation is not NumPy array")
    if np.isinf(observation).any():
        warnings.warn("Observation contains infinity (np.inf) or negative infinity (-np.inf)")
    if np.isnan(observation).any():
        warnings.warn("Observation contains NaNs")
    if len(observation.shape) > 3:
        warnings.warn("Observation has more than 3 deminsions")
    if observation.shape == (0,):
        raise Exception("Observation is empty array")
    if observation.shape == (1,):
        warnings.warn("Observation is a single number")


def mandatory_tests(env):
    assert isinstance(env, pettingzoo.AECEnv)
    observation = env.reset()
    test_obervation(observation)
    agent = env.agent_order[0]
    action = env.action_spaces[agent].sample()
    observation = env.step(action)
    test_obervation(observation)

    # check observe = False stuff
    # check last_cycle
    # check attributes/methods and types
    # look at my PR to SB and what they actually used