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


from .pursuit import pursuit as pursuit_v0
from .waterworld import waterworld as waterworld_v0
from .multiwalker import multiwalker as multiwalker_v0
