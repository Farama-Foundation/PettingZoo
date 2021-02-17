from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_reference import Scenario
from pettingzoo.utils.conversions import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, local_ratio=0.5, max_cycles=25):
        assert 0. <= local_ratio <= 1., "local_ratio is a proportion. Must be between 0 and 1."
        scenario = Scenario()
        world = scenario.make_world()
        super().__init__(scenario, world, max_cycles, local_ratio)
        self.metadata['name'] = "simple_reference_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
