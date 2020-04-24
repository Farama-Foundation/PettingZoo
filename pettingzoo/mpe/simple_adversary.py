from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple_adversary import Scenario


class env(SimpleEnv):
    def __init__(self, seed=None, N=2, max_frames=100):
        scenario = Scenario()
        world = scenario.make_world(N=2)
        super(env, self).__init__(scenario, world, max_frames, seed)
