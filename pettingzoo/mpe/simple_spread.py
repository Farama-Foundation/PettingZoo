from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple_spread import Scenario


class env(SimpleEnv):
    def __init__(self, N=3, max_frames=500):
        scenario = Scenario()
        world = scenario.make_world(N)
        super(env, self).__init__(scenario, world, max_frames)
