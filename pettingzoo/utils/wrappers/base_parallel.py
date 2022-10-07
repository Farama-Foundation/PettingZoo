import warnings

from gymnasium.utils import seeding

from ..env import ParallelEnv


class BaseParallelWraper(ParallelEnv):
    def __init__(self, env):
        self.env = env

        self.metadata = env.metadata
        try:
            self.possible_agents = env.possible_agents
        except AttributeError:
            pass

        # Not every environment has the .state_space attribute implemented
        try:
            self.state_space = self.env.state_space
        except AttributeError:
            pass

    def reset(self, seed=None, return_info=False, options=None):
        self.np_random, _ = seeding.np_random(seed)

        if not return_info:
            res = self.env.reset(seed=seed, options=options)
            self.agents = self.env.agents
            return res
        else:
            res, info = self.env.reset(
                seed=seed, return_info=return_info, options=options
            )
            self.agents = self.env.agents
            return res, info

    def step(self, actions):
        res = self.env.step(actions)
        self.agents = self.env.agents
        return res

    def render(self):
        return self.env.render()

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
            return {
                agent: self.observation_space(agent) for agent in self.possible_agents
            }
        except AttributeError as e:
            raise AttributeError(
                "The base environment does not have an `observation_spaces` dict attribute. Use the environments `observation_space` method instead"
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
                "The base environment does not have an action_spaces dict attribute. Use the environments `action_space` method instead"
            ) from e

    def observation_space(self, agent):
        return self.env.observation_space(agent)

    def action_space(self, agent):
        return self.env.action_space(agent)
