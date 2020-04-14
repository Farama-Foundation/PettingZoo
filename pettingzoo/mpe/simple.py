from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple import Scenario


class env(SimpleEnv):
    def __init__(self, max_frames=500, random_seed=None):
        scenario = Scenario()
        world = scenario.make_world()
        super(env, self).__init__(scenario, world, max_frames, random_seed)
