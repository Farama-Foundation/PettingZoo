from pettingzoo.utils.vector.vector_env import VectorAECWrapper
from pettingzoo.utils.vector.async_vector_env import ProcVectorEnv

from pettingzoo.classic import rps_v0
from pettingzoo.classic import mahjong_v0
from pettingzoo.gamma import knights_archers_zombies_v0
from pettingzoo.mpe import simple_world_comm_v0
from pettingzoo.sisl import multiwalker_v0
from copy import copy
import numpy as np
import random

class constr_obj:
    def __init__(self, env_constr, seed):
        self.seed = seed
        self.env_constr = env_constr
    def __call__(self):
        if self.seed is None:
            return self.env_constr()
        else:
            return self.env_constr(seed=self.seed)

def assert_states_equal(vec_env1, vec_env2):
    assert all(np.all(np.equal(vec_env1.dones[agent], vec_env2.dones[agent])) for agent in vec_env1.agents)
    assert all(np.all(np.equal(vec_env1.rewards[agent], vec_env2.rewards[agent])) for agent in vec_env1.agents)
    assert vec_env1.infos == vec_env2.infos
    assert vec_env1.agent_selection == vec_env2.agent_selection

def test_async_vector_env(env_constructor, should_seed):
    NUM_ENVS = 5
    NUM_CPUS = 2
    RNG_SEED = 0x2141 if should_seed else None
    constructors = [constr_obj(env_constructor,RNG_SEED+i if should_seed else None) for i in range(NUM_ENVS)]
    vecenv = VectorAECWrapper(constructors)
    asyncenv = ProcVectorEnv(constructors, NUM_CPUS)
    cycles = 200
    vec_obs,vec_pass = vecenv.reset()
    async_obs,asyc_pass = asyncenv.reset()
    obs_dtype = vecenv.observation_spaces[vecenv.agent_selection]

    assert np.all(np.equal(vec_pass, asyc_pass))
    all_equal = np.all(np.equal(np.asarray(vec_obs,dtype=obs_dtype),async_obs))
    if not all_equal:
        print(vec_obs)
        print(async_obs)
    assert all_equal
    assert_states_equal(vecenv, asyncenv)

    for i in range(cycles):
        actions = []
        for i in range(NUM_ENVS):
            agent = vecenv.agent_selection
            cur_info = vecenv.infos[agent][i]

            if 'legal_moves' in cur_info and not vec_pass[i]:
                action = random.choice(cur_info['legal_moves'])
            else:
                action = vecenv.action_spaces[agent].sample()
            actions.append(action)

        vec_obs = vecenv.observe(vecenv.agent_selection)
        async_obs = asyncenv.observe(asyncenv.agent_selection)
        assert np.all(np.equal(np.asarray(vec_obs,dtype=obs_dtype), async_obs))

        vec_obs,vec_pass,vec_dones = vecenv.step(actions)
        async_obs,asyc_pass,async_dones = asyncenv.step(actions)

        assert np.all(np.equal(vec_dones, async_dones))
        assert np.all(np.equal(vec_pass, asyc_pass))
        assert np.all(np.equal(np.array(vec_obs,dtype=obs_dtype)[(1^np.array(vec_pass)).astype(np.bool)], np.array(async_obs)[(1^np.array(asyc_pass)).astype(np.bool)]))
        assert_states_equal(vecenv, asyncenv)

        # if all(env.dones.values()):
        #     vec_obs = vecenv.reset()
        #     async_obs = asyncenv.reset()
        #     assert np.all(np.equal(vec_obs, async_obs))
        #     assert_states_equal(vecenv, asyncenv)
        #     break

def test_all():
    print("rps_v0 test started")
    test_async_vector_env((rps_v0.env), False)
    print("mahjong_v0 test started")
    test_async_vector_env((mahjong_v0.env), True)
    print("multiwalker_v0 test started")
    test_async_vector_env((multiwalker_v0.env), True)
    print("simple_world_comm_v0 test started")
    test_async_vector_env((simple_world_comm_v0.env), True)
