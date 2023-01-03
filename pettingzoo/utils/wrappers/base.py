import warnings

from pettingzoo.utils.env import AECEnv


class BaseWrapper(AECEnv):
    """Creates a wrapper around `env` parameter.

    All AECEnv wrappers should inherit from this base class
    """

    def __init__(self, env):
        super().__init__()
        self.env = env

        try:
            self.possible_agents = self.env.possible_agents
        except AttributeError:
            pass

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

    def __getattr__(self, name):
        """Returns an attribute with ``name``, unless ``name`` starts with an underscore."""
        if name.startswith("_"):
            raise AttributeError(f"accessing private attribute '{name}' is prohibited")
        return getattr(self.env, name)

    @property
    def observation_spaces(self):
        warnings.warn(
            "The `observation_spaces` dictionary is deprecated. Use the `observation_space` function instead."
        )
        try:
            return {
                agent: self.observation_space(agent) for agent in self.possible_agents
            }
        except AttributeError as e:
            raise AttributeError(
                "The base environment does not have an `observation_spaces` dict attribute. Use the environment's `observation_space` method instead"
            ) from e

    @property
    def action_spaces(self):
        warnings.warn(
            "The `action_spaces` dictionary is deprecated. Use the `action_space` function instead."
        )
        try:
            return {agent: self.action_space(agent) for agent in self.possible_agents}
        except AttributeError as e:
            raise AttributeError(
                "The base environment does not have an action_spaces dict attribute. Use the environment's `action_space` method instead"
            ) from e

    def observation_space(self, agent):
        return self.env.observation_space(agent)

    def action_space(self, agent):
        return self.env.action_space(agent)

    @property
    def unwrapped(self):
        return self.env.unwrapped

    def close(self):
        self.env.close()

    def render(self):
        return self.env.render()

    def reset(self, seed=None, return_info=False, options=None):
        self.env.reset(seed=seed, options=options)

        self.agent_selection = self.env.agent_selection
        self.rewards = self.env.rewards
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
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
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos
        self.agents = self.env.agents
        self._cumulative_rewards = self.env._cumulative_rewards

    def __str__(self):
        """Returns a name which looks like: "max_observation<space_invaders_v1>"."""
        return f"{type(self).__name__}<{str(self.env)}>"
