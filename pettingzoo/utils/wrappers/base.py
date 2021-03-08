from pettingzoo.utils.env import AECEnv


class BaseWrapper(AECEnv):
    '''
    Creates a wrapper around `env` parameter. Extend this class
    to create a useful wrapper.
    '''

    def __init__(self, env):
        super().__init__()
        self.env = env

        self.observation_spaces = self.env.observation_spaces
        self.action_spaces = self.env.action_spaces
        self.possible_agents = self.env.possible_agents
        self.metadata = self.env.metadata

        # we don't want these defined as we don't want them used before they are gotten

        # self.agent_selection = self.env.agent_selection

        # self.rewards = self.env.rewards
        # self.dones = self.env.dones

        # we don't want to care one way or the other whether environments have an infos or not before reset
        try:
            self.infos = self.env.infos
        except AttributeError:
            pass

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.env.state_space
        except AttributeError:
            pass

    @property
    def unwrapped(self):
        return self.env.unwrapped

    def seed(self, seed=None):
        self.env.seed(seed)

    def close(self):
        self.env.close()

    def render(self, mode='human'):
        return self.env.render(mode)

    def reset(self):
        self.env.reset()

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos
        self.agents = self.env.agents
        self._cumulative_rewards = self.env._cumulative_rewards

    def observe(self, agent):
        return self.env.observe(agent)

    def state(self):
        return self.env.state()

    def step(self, action):
        self.env.step(action)

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos
        self.agents = self.env.agents
        self._cumulative_rewards = self.env._cumulative_rewards

    def __str__(self):
        '''
        returns a name which looks like: "max_observation<space_invaders_v1>"
        '''
        return '{}<{}>'.format(type(self).__name__, str(self.env))
