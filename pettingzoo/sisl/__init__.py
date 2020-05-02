class Agent(object):

    def __new__(cls, *args, **kwargs):
        agent = super(Agent, cls).__new__(cls)
        return agent

    @property
    def observation_space(self):
        raise NotImplementedError()

    @property
    def action_space(self):
        raise NotImplementedError()

    def __str__(self):
        return '<{} instance>'.format(type(self).__name__)


from .pursuit import pursuit
from .waterworld import waterworld as waterworld_v0
from .multiwalker import multiwalker as multiwalker_v0

class pursuit_v0:
    @staticmethod
    def env(**kwargs):
        env = chess_env.env(**kwargs)
        env = TerminateIllegalWrapper(env,illegal_reward=-1)
        env = AssertOutOfBoundsWrapper(env)
        env = TerminateNaNWrapper(env)
        env = OrderEnforcingWrapper(env)
        return env
