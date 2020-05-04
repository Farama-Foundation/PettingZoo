import warnings
import random
import numpy as np


def check_environment_deterministic(env1, env2):
    '''
    env1 and env2 should be seeded environments

    returns a bool: true if env1 and env2 execute the same way
    '''

    # checks deterministic behavior if seed is set
    actions = {agent: space.sample() for agent, space in env1.action_spaces.items()}
    hashes = []
    num_seeds = 2
    envs = [env1, env2]
    for x in range(num_seeds):
        new_env = envs[x]
        cur_hashes = []
        obs = new_env.reset()
        for i in range(x + 1):
            random.randint(0, 1000)
            np.random.normal(size=100)
        cur_hashes.append(hash_obsevation(obs))
        for _ in range(50):
            rew, done, info = new_env.last()
            if done:
                break
            next_obs = new_env.step(actions[new_env.agent_selection])
            cur_hashes.append(hash_obsevation(next_obs))

        hashes.append(hash(tuple(cur_hashes)))

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


def seed_test(env_constructor):
    try:
        env_constructor(seed=None)
    except Exception:
        if not check_environment_deterministic(env_constructor(), env_constructor()):
            warnings.warn("The environment gives different results on multiple runs and does not have a `seed` argument. Environments which use random values should take a seed as an argument.")
        return

    base_seed = 42
    if not check_environment_deterministic(env_constructor(seed=base_seed), env_constructor(seed=base_seed)):
        warnings.warn("The environment gives different results on multiple runs when intialized with the same seed. This is usually a sign that you are using np.random or random modules directly, which uses a global random state.")
    if check_environment_deterministic(env_constructor(), env_constructor()):
        warnings.warn("The environment gives same results on multiple runs when intialized by default. By default, environments that take a seed argument should be nondeterministic")
