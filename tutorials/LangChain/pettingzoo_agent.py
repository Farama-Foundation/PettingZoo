import inspect

from gymnasium_agent import GymnasiumAgent


class PettingZooAgent(GymnasiumAgent):
    @classmethod
    def get_docs(cls, env):
        return inspect.getmodule(env.unwrapped).__doc__

    def __init__(self, name, model, env):
        super().__init__(model, env)
        self.name = name

    def random_action(self):
        action = self.env.action_space(self.name).sample()
        return action
