from pettingzoo.utils.env import AECEnv
from pettingzoo.utils._parallel_env import _parallel_env_wrapper
from pettingzoo.utils.wrappers import OrderEnforcingWrapper
from pettingzoo.utils.env import ParallelEnv


class to_parallel(ParallelEnv):
    def __init__(self, aec_env):
        self.aec_env = aec_env
        self.observation_spaces = aec_env.observation_spaces
        self.action_spaces = aec_env.action_spaces
        self.agents = aec_env.agents
        self.num_agents = aec_env.num_agents
        self._was_dones = {agent: False for agent in self.agents}

    def seed(self, seed=None):
        return self.aec_env.seed(seed)

    def reset(self):
        self.aec_env.reset(observe=False)
        self._was_dones = {agent: False for agent in self.agents}
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents if not self.aec_env.dones[agent]}
        return observations

    def step(self, actions):
        rewards = {}
        dones = {}
        infos = {}

        stepped_agents = set()
        while (self.aec_env.agent_selection not in stepped_agents and self.aec_env.dones[self.aec_env.agent_selection]):
            agent = self.aec_env.agent_selection
            self.aec_env.step(None)
            stepped_agents.add(agent)

        stepped_agents = set()
        while (self.aec_env.agent_selection not in stepped_agents):
            agent = self.aec_env.agent_selection
            assert agent in actions or self.aec_env.dones[agent], \
                "Live environment agent is not in actions dictionary"
            self.aec_env.step(actions.get(agent, None))
            stepped_agents.add(agent)

        assert all(agent in stepped_agents or self.aec_env.dones[agent]
                   for agent in actions), \
            "environment has a nontrivial ordering, and cannot be used with"\
            " the POMGameEnv wrapper"

        rewards = self.aec_env.rewards
        dones = self.aec_env.dones
        infos = self.aec_env.infos
        observations = {agent: self.aec_env.observe(agent) for agent in self.aec_env.agents}
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        return self.aec_env.render(mode)

    def close(self):
        return self.aec_env.close()


def parallel_wrapper_fn(env_fn):
    def par_fn(**kwargs):
        env = env_fn(**kwargs)
        env = to_parallel(env)
        return env
    return par_fn


def from_parallel(par_env):
    if isinstance(par_env, to_parallel):
        return par_env.aec_env
    else:
        aec_env = _parallel_env_wrapper(par_env)
        ordered_env = OrderEnforcingWrapper(aec_env)
        return ordered_env
