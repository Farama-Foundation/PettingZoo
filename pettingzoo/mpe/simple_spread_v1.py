from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_spread import Scenario
from pettingzoo.utils.to_parallel import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, N=3, local_ratio=0.5, max_frames=25):
        assert 0. <= local_ratio <= 1., "local_ratio is a proportion. Must be between 0 and 1."
        scenario = Scenario()
        world = scenario.make_world(N)
        super().__init__(scenario, world, max_frames, local_ratio)


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
