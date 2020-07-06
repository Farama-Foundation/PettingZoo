from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_adversary import Scenario


class raw_env(SimpleEnv):
    def __init__(self, seed=None, N=2, max_frames=100):
        scenario = Scenario()
        world = scenario.make_world(N=2)
        super().__init__(scenario, world, max_frames, seed)


env = make_env(raw_env)
