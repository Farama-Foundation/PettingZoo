import warnings

from ..env import ParallelEnv


class BaseParallelWraper(ParallelEnv):
    def __init__(self, env):
        self.env = env
        # try to access these parameters for backwards compatability
        try:
            self._observation_spaces = self.env.observation_spaces
            self._action_spaces = self.env.action_spaces
        except AttributeError:
            pass

        self.metadata = env.metadata
        try:
            self.possible_agents = env.possible_agents
        except AttributeError:
            pass

    def reset(self):
        res = self.env.reset()
        self.agents = self.env.agents
        return res

    def step(self, actions):
        res = self.env.step(actions)
        self.agents = self.env.agents
        return res

    def render(self, mode="human"):
        return self.env.render(mode)

    def close(self):
        return self.env.close()

    @property
    def unwrapped(self):
        return self.env.unwrapped

    def state(self):
        return self.env.state()

    @property
    def observation_spaces(self):
        warnings.warn(
            "The `observation_spaces` dictionary is deprecated. Use the `observation_space` function instead."
        )
        try:
            return self._observation_spaces
        except AttributeError:
            raise AttributeError(
                "The base environment does not have an `observation_spaces` dict attribute. Use the environments `observation_space` method instead"
            )

    @property
    def action_spaces(self):
        warnings.warn(
            "The `action_spaces` dictionary is deprecated. Use the `action_space` function instead."
        )
        try:
            return self._action_spaces
        except AttributeError:
            raise AttributeError(
                "The base environment does not have an action_spaces dict attribute. Use the environments `action_space` method instead"
            )

    def observation_space(self, agent):
        return self.env.observation_space(agent)

    def action_space(self, agent):
        return self.env.action_space(agent)
