from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_adversary import Scenario
from pettingzoo.utils.to_parallel import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, N=2, max_frames=25):
        scenario = Scenario()
        world = scenario.make_world(N=2)
        super().__init__(scenario, world, max_frames)


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
