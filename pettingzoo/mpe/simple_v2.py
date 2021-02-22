from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple import Scenario
from pettingzoo.utils.conversions import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, max_cycles=100):
        scenario = Scenario()
        world = scenario.make_world()
        super().__init__(scenario, world, max_cycles)
        self.metadata['name'] = "simple_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
