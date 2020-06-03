import copy
import multiprocessing as mp
from gym.vector.utils import shared_memory
from pettingzoo.utils.agent_selector import agent_selector
import numpy as np
import ctypes
import gym
from .vector_env import VectorAECWrapper
import warnings
import signal


class SharedData:
    def __init__(self, array, num_envs, shape, dtype):
        self.array = array
        self.num_envs = num_envs
        self.nparr = np.frombuffer(array,
            dtype=dtype).reshape((num_envs,) + shape)

def create_shared_data(num_envs, obs_space, act_space):
    obs_array = mp.Array(np.ctypeslib.as_ctypes_type(obs_space.dtype),int(num_envs*np.prod(obs_space.shape)),lock=False)
    act_array = mp.Array(np.ctypeslib.as_ctypes_type(act_space.dtype),int(num_envs*np.prod(act_space.shape)),lock=False)
    rew_array = mp.Array(ctypes.c_double,num_envs,lock=False)
    done_array = mp.Array(ctypes.c_bool,num_envs,lock=False)
    data = (obs_array,act_array,rew_array,done_array)
    return data

def create_env_data(num_envs):
    env_dones = mp.Array(ctypes.c_bool,num_envs,lock=False)
    agent_sel_idx = mp.Array(ctypes.c_uint,num_envs,lock=False)
    return env_dones,agent_sel_idx

class SpaceWrapper:
    def __init__(self, space):
        if isinstance(space, gym.spaces.Discrete):
            self.shape = ()
            self.dtype = np.dtype(np.int32)
        elif isinstance(space, gym.spaces.Box):
            self.shape = space.shape
            self.dtype = np.dtype(space.dtype)
        else:
            assert False, "ProcVectorEnv only support Box and Discrete types"

class AgentSharedData:
    def __init__(self, num_envs, obs_space, act_space, data):
        self.num_envs = num_envs

        obs_array,act_array,rew_array,done_array = data
        self.obs = SharedData(obs_array, num_envs, obs_space.shape, obs_space.dtype)
        self.act = SharedData(act_array, num_envs, act_space.shape, act_space.dtype)
        self.rewards = SharedData(rew_array, num_envs, (), np.float64)
        self.dones = SharedData(done_array, num_envs, (), np.bool)

class EnvSharedData:
    def __init__(self, num_envs, data):
        env_dones,agent_idx_array = data
        self.env_dones = SharedData(env_dones, num_envs, (), np.bool)
        self.agent_sel_idx = SharedData(agent_idx_array, num_envs, (), np.uint32)


class _SeperableAECWrapper:
    def __init__(self, env_constructors, num_envs):
        self.envs = [env_constructor() for env_constructor in env_constructors]
        self.env = self.envs[0]
        self.agents = self.env.agents
        self.agent_indexes = {agent:i for i, agent in enumerate(self.env.agents)}

    def reset(self, observe):
        observations = []
        for env in self.envs:
            observations.append(env.reset(observe))

        self.rewards = {agent: [env.rewards[agent] for env in self.envs] for agent in self.agents}
        self.dones = {agent: [env.dones[agent] for env in self.envs] for agent in self.agents}
        self.infos = {agent: [env.infos[agent] for env in self.envs] for agent in self.agents}

        return (observations if observe else None)

    def observe(self, agent):
        observations = []
        for env in self.envs:
            observations.append(env.observe(agent))
        return observations

    def step(self, agent_step, actions, observe):
        assert len(actions) == len(self.envs)

        observations = []
        for act,env in zip(actions,self.envs):
            observations.append(env.step(act,observe) if env.agent_selection == agent_step else None)

        self.rewards = {agent: [env.rewards[agent] for env in self.envs] for agent in self.agents}
        self.dones = {agent: [env.dones[agent] for env in self.envs] for agent in self.agents}
        self.infos = {agent: [env.infos[agent] for env in self.envs] for agent in self.agents}

        env_dones = [all(env.dones.values()) for env in self.envs]

        for i in range(len(self.envs)):
            if env_dones[i]:
                observations[i] = self.envs[i].reset(observe)

        return (observations if observe else None),env_dones

    def get_agent_indexes(self):
        return [self.agent_indexes[env.agent_selection] for env in self.envs]


def sig_handle(signal_object, argvar):
    raise RuntimeError()

has_initted = False
def init_parallel_env():
    global has_initted
    if not has_initted:
        signal.signal(signal.SIGINT, sig_handle)
        signal.signal(signal.SIGTERM, sig_handle)

def write_out_data(rewards, dones, num_envs, start_index, shared_data):
    for agent in shared_data:
        rews = np.asarray(rewards[agent],dtype=np.float64)
        dns = np.asarray(dones[agent],dtype=np.bool)
        cur_data = shared_data[agent]
        cur_data.rewards.nparr[start_index:start_index+num_envs] = rews
        cur_data.dones.nparr[start_index:start_index+num_envs] = dns

def write_env_data(env_dones, indexes, num_envs, start_index, shared_data):
    shared_data.env_dones.nparr[start_index:start_index+num_envs] = env_dones
    agent_indexes = np.asarray(indexes,dtype=np.uint32)
    shared_data.agent_sel_idx.nparr[start_index:start_index+num_envs] = agent_indexes

def write_obs(obs, num_env, start_index, shared_data):
    for i,o in enumerate(obs):
        if o is not None:
            shared_data.obs.nparr[start_index+i] = o

def compress_info(infos):
    all_infos = {}
    for agent, infs in infos.items():
        non_empty_infs = [(i,info) for i,info in enumerate(infs) if info]
        if non_empty_infs:
            all_infos[agent] = non_empty_infs
    return all_infos

def decompress_info(agents, num_envs, idx_starts, comp_infos):
    all_info = {agent:[{}]*num_envs for agent in agents}
    for idx_start, comp_info in zip(idx_starts,comp_infos):
        for agent, inf_data in comp_info.items():
            agent_info = all_info[agent]
            for i,info in inf_data:
                agent_info[idx_start+i] = info
    return all_info


def env_worker(env_constructors, total_num_envs, idx_start, my_num_envs, agent_arrays, env_arrays, pipe):
    env = _SeperableAECWrapper(env_constructors, my_num_envs)
    shared_datas = {agent: AgentSharedData(total_num_envs,
                                SpaceWrapper(env.env.observation_spaces[agent]),
                                SpaceWrapper(env.env.action_spaces[agent]),
                                agent_arrays[agent])
                        for agent in env.agents}

    env_datas = EnvSharedData(total_num_envs, env_arrays)


    while True:
        #pipe.close()
        instruction, data = pipe.recv()
        if instruction == "reset":
            do_observe = data
            obs = env.reset(do_observe)
            write_out_data(env.rewards,env.dones,my_num_envs,idx_start,shared_datas)
            env_dones = np.zeros(my_num_envs,dtype=np.bool)
            write_env_data(env_dones,env.get_agent_indexes(),my_num_envs, idx_start, env_datas)
            if do_observe:
                # this observation gets overridden if the agent_selection is non-deterministic
                agent_observe = env.envs[0].agent_selection
                write_obs(obs, my_num_envs, idx_start, shared_datas[agent_observe])

            pipe.send(compress_info(env.infos))

        elif instruction == "observe":
            agent_observe = data
            obs = env.observe(agent_observe)
            write_obs(obs, my_num_envs, idx_start, shared_datas[agent_observe])

            pipe.send(True)
        elif instruction == "step":
            step_agent, do_observe = data

            actions = shared_datas[step_agent].act.nparr[idx_start:idx_start+my_num_envs]

            obs,env_dones = env.step(step_agent, actions, do_observe)
            write_out_data(env.rewards,env.dones,my_num_envs,idx_start,shared_datas)
            write_env_data(env_dones, env.get_agent_indexes(), my_num_envs, idx_start, env_datas)
            if do_observe:
                agent_observe = env.envs[0].agent_selection
                write_obs(obs, my_num_envs, idx_start, shared_datas[agent_observe])

            pipe.send(compress_info(env.infos))
        elif instruction == "terminate":
            return
        else:
            assert False, "Bad instruction sent to ProcVectorEnv worker"

class ProcVectorEnv(VectorAECWrapper):
    def __init__(self, env_constructors, num_cpus=None):
        # set signaling so that crashing is handled gracefully
        init_parallel_env()

        num_envs = len(env_constructors)

        if num_cpus is None:
            num_cpus = mp.cpu_count()

        num_cpus = min(num_cpus, num_envs)
        assert num_envs > 0

        assert num_envs >= 1
        assert callable(env_constructors[0]), "env_constructor must be a callable object (i.e function) that create an environment"
        #self.envs = [env_constructor() for _ in range(num_envs)]
        self.env = env = env_constructors[0]()
        self.num_agents = self.env.num_agents
        self.agents = self.env.agents
        self.observation_spaces = copy.copy(self.env.observation_spaces)
        self.action_spaces = copy.copy(self.env.action_spaces)
        self.order_is_nondeterministic = False
        self.num_envs = num_envs

        self.agent_indexes = {agent:i for i, agent in enumerate(self.env.agents)}

        self._agent_selector = agent_selector(self.agents)

        all_arrays = {agent: create_shared_data(
                                num_envs,
                                SpaceWrapper(self.observation_spaces[agent]),
                                SpaceWrapper(self.action_spaces[agent]),
                            )
                            for agent in self.agents}

        self.shared_datas = {agent: AgentSharedData(num_envs,
                                    SpaceWrapper(env.observation_spaces[agent]),
                                    SpaceWrapper(env.action_spaces[agent]),
                                    all_arrays[agent])
                            for agent in env.agents}

        env_arrays = create_env_data(num_envs)

        self.env_datas = EnvSharedData(num_envs, env_arrays)

        self.procs = []
        self.pipes = [mp.Pipe() for _ in range(num_cpus)]
        self.con_ins = [con_in for con_in,con_out in self.pipes]
        self.con_outs = [con_out for con_in,con_out in self.pipes]
        self.env_starts = []
        env_counter = 0
        for pidx in range(num_cpus):
            envs_left = num_envs - env_counter
            allocated_envs = min(envs_left,(num_envs+num_cpus-1)//num_cpus)
            proc_constructors = env_constructors[env_counter:env_counter+allocated_envs]
            proc = mp.Process(target=env_worker,args=(proc_constructors, num_envs, env_counter, allocated_envs, all_arrays, env_arrays, self.con_outs[pidx]))
            self.procs.append(proc)
            self.env_starts.append(env_counter)

            proc.start()
            env_counter += allocated_envs

    def _find_active_agent(self):
        cur_selection = self.agent_selection
        while not np.any(np.equal(self.agent_indexes[cur_selection], self.env_datas.agent_sel_idx.nparr)):
            cur_selection = self._agent_selector.next()
        return cur_selection

    def _load_next_data(self, observe, reset):
        all_compressed_info = []
        for cin in self.con_ins:
            compressed_info = cin.recv()
            all_compressed_info.append(compressed_info)

        all_info = decompress_info(self.agents, self.num_envs, self.env_starts, all_compressed_info)

        self.agent_selection = self._agent_selector.reset() if reset else self._agent_selector.next()
        self.agent_selection = self._find_active_agent()

        obs = self.shared_datas[self.agent_selection].obs.nparr
        passes = np.not_equal(self.env_datas.agent_sel_idx.nparr, self.agent_indexes[self.agent_selection])

        assert not np.all(passes), "something went wrong with finding agent"
        if np.any(passes) or self.order_is_nondeterministic:
            warnings.warn("agent order of environment is werid, so the ProcVectorEnv has to do more work, expect it to be slower than expected")
            if observe:
                obs = self.observe(self.agent_selection)
            self.order_is_nondeterministic = True

        self.dones = {agent: np.copy(self.shared_datas[agent].dones.nparr) for agent in self.agents}
        self.rewards = {agent: np.copy(self.shared_datas[agent].rewards.nparr) for agent in self.agents}
        self.infos = all_info
        env_dones = self.env_datas.env_dones.nparr

        return (np.copy(obs) if observe else None), np.copy(passes), np.copy(env_dones)

    def reset(self, observe=True):
        for cin in self.con_ins:
            cin.send(("reset", observe))

        return self._load_next_data(observe, True)[:2]

    def step(self, actions, observe=True):
        step_agent = self.agent_selection

        self.shared_datas[self.agent_selection].act.nparr[:] = actions
        for cin in self.con_ins:
            cin.send(("step", (step_agent, observe)))

        return self._load_next_data(observe, False)

    def observe(self, agent):
        for cin in self.con_ins:
            cin.send(("observe", agent))

        # wait until all are finished
        for cin in self.con_ins:
            cin.recv()

        obs = np.copy(self.shared_datas[self.agent_selection].obs.nparr)
        return obs

    def __del__(self):
        for cin in self.con_ins:
            cin.send(("terminate", None))
        for proc in self.procs:
            proc.join()
