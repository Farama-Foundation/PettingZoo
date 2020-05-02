

def check_environment_deterministic(env1, env2):
    '''
    env1 and env2 should be seeded environments

    returns a bool: true if env1 and env2 execute the same way
    '''

    # checks deterministic behavior if seed is set
    actions = {agent: space.sample() for agent, space in env1.action_spaces.items()}
    hashes = []
    num_seeds = 5
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
        new_env = env.__class__(seed=base_seed)

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
