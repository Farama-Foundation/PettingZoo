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
            elif isinstance(obs, dict) and 'action_mask' in obs:
                action = sampler.choice(np.flatnonzero(obs['action_mask']))
            else:
                action = new_env.action_spaces[agent].sample()
            new_env.step(action)
            cur_hashes.append(hash_obsevation(obs))
            cur_hashes.append(float(rew))

    return hash(tuple(cur_hashes))


def seed_action_spaces(env):
    for i, (agent, space) in enumerate(sorted(env.action_spaces.items())):
        space.seed(42 + i)


def check_environment_deterministic(env1, env2, num_cycles):
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
    max_env_iters = num_cycles * len(env1.possible_agents)
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
    env1.seed(42)
    env1.reset()
    hash1 = calc_hash(env1, 1, num_cycles)
    seed_action_spaces(env1)
    env1.seed(42)
    env1.reset()
    hash2 = calc_hash(env1, 2, num_cycles)
    assert hash1 == hash2, "environments kept state after seed(42) and reset()"


def seed_test(env_constructor, num_cycles=10, test_kept_state=True):
    env1 = env_constructor()
    if test_kept_state:
        test_environment_reset_deterministic(env1, num_cycles)
    env2 = env_constructor()
    base_seed = 42
    env1.seed(base_seed)
    env2.seed(base_seed)

    assert check_environment_deterministic(env1, env2, num_cycles), \
        ("The environment gives different results on multiple runs when intialized with the same seed. This is usually a sign that you are using np.random or random modules directly, which uses a global random state.")
