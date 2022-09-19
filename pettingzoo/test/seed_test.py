import hashlib
import pickle
import random
import warnings

import numpy as np

from pettingzoo.utils import parallel_to_aec


def hash(val):
    val = pickle.dumps(val)
    hasher = hashlib.md5()
    hasher.update(val)
    return hasher.hexdigest()


def calc_hash(new_env, rand_issue, max_env_iters):
    cur_hashes = []
    sampler = random.Random(42)
    for i in range(3):
        new_env.reset(seed=i)
        for j in range(rand_issue + 1):
            random.randint(0, 1000)
            np.random.normal(size=100)
        for agent in new_env.agent_iter(max_env_iters):
            obs, rew, terminated, truncated, info = new_env.last()
            if terminated or truncated:
                action = None
            elif isinstance(obs, dict) and "action_mask" in obs:
                action = sampler.choice(np.flatnonzero(obs["action_mask"]))
            else:
                action = new_env.action_space(agent).sample()
            new_env.step(action)
            cur_hashes.append(agent)
            cur_hashes.append(hash_obsevation(obs))
            cur_hashes.append(float(rew))

    return hash(tuple(cur_hashes))


def seed_action_spaces(env):
    if hasattr(env, "possible_agents"):
        for i, agent in enumerate(env.possible_agents):
            env.action_space(agent).seed(42 + i)


def check_environment_deterministic(env1, env2, num_cycles):
    """
    env1 and env2 should be seeded environments

    returns a bool: true if env1 and env2 execute the same way
    """

    # seeds action space so that actions are deterministic
    seed_action_spaces(env1)
    seed_action_spaces(env2)

    num_agents = max(1, len(getattr(env1, "possible_agents", [])))

    # checks deterministic behavior if seed is set
    hashes = []
    num_seeds = 2
    max_env_iters = num_cycles * num_agents
    envs = [env1, env2]
    for x in range(num_seeds):
        hashes.append(calc_hash(envs[x], x, max_env_iters))

    return all(hashes[0] == h for h in hashes)


def hash_obsevation(obs):
    try:
        val = hash(obs.tobytes())
        return val
    except AttributeError:
        try:
            return hash(obs)
        except TypeError:
            warnings.warn("Observation not an int or an Numpy array")
            return 0


def test_environment_reset_deterministic(env1, num_cycles):
    seed_action_spaces(env1)
    hash1 = calc_hash(env1, 1, num_cycles)
    seed_action_spaces(env1)
    hash2 = calc_hash(env1, 2, num_cycles)
    assert hash1 == hash2, "environments kept state after and reset(seed)"


def seed_test(env_constructor, num_cycles=10, test_kept_state=True):
    env1 = env_constructor()
    if test_kept_state:
        test_environment_reset_deterministic(env1, num_cycles)
    env2 = env_constructor()

    assert check_environment_deterministic(
        env1, env2, num_cycles
    ), "The environment gives different results on multiple runs when initialized with the same seed. This is usually a sign that you are using np.random or random modules directly, which uses a global random state."


def parallel_seed_test(parallel_env_fn, num_cycles=10, test_kept_state=True):
    def aec_env_fn():
        parallel_env = parallel_env_fn()
        env = parallel_to_aec(parallel_env)
        return env

    seed_test(aec_env_fn, num_cycles, test_kept_state)
