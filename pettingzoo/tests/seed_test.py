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
        for i in range(3):
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
                cur_hashes.append(float(rew))

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
    env1 = env_constructor()
    env2 = env_constructor()
    base_seed = 42
    env1.seed(base_seed)
    env2.seed(base_seed)

    assert check_environment_deterministic(env1, env2), \
         ("The environment gives different results on multiple runs when intialized with the same seed. This is usually a sign that you are using np.random or random modules directly, which uses a global random state.")

    env1.seed(base_seed)
    env2.seed(base_seed+1)
    if check_environment_deterministic(env1, env2):
        warnings.warn("The environment gives same results on multiple runs when intialized by default. By default, environments that take a seed argument should be nondeterministic")
