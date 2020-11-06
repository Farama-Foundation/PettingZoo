import warnings
import random
import numpy as np
import hashlib
import pickle


def hash(val):
    val = pickle.dumps(val)
    hasher = hashlib.md5()
    hasher.update(val)
    return hasher.hexdigest()


def calc_hash(new_env, rand_issue, max_env_iters):
    cur_hashes = []
    sampler = random.Random(42)
    for i in range(3):
        new_env.reset()
        for j in range(rand_issue + 1):
            random.randint(0, 1000)
            np.random.normal(size=100)
        for agent in new_env.agent_iter(max_env_iters):
            obs, rew, done, info = new_env.last()
            if done:
                action = None
            elif 'legal_moves' in info:
                action = sampler.choice(info['legal_moves'])
            else:
                action = new_env.action_spaces[agent].sample()
            new_env.step(action)
            cur_hashes.append(hash_obsevation(obs))
            cur_hashes.append(float(rew))

    return hash(tuple(cur_hashes))


def seed_action_spaces(env):
    for space in env.action_spaces.values():
        space.seed(42)


def check_environment_deterministic(env1, env2):
    '''
    env1 and env2 should be seeded environments

    returns a bool: true if env1 and env2 execute the same way
    '''

    # seeds action space so that actions are deterministic
    seed_action_spaces(env1)
    seed_action_spaces(env2)

    # checks deterministic behavior if seed is set
    hashes = []
    num_seeds = 2
    max_env_iters = 50
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
